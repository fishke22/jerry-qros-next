using System;
using System.Globalization;
using System.IO;
using QuantConnect;
using QuantConnect.Algorithm;
using QuantConnect.Data;

namespace Qros.Lean.Synthetic;

public sealed class QrosSyntheticBacktestAlgorithm : QCAlgorithm
{
    private int _rows;
    private decimal _sum;
    private decimal _last;

    public override void Initialize()
    {
        SetStartDate(2026, 1, 5);
        SetEndDate(2026, 1, 10);
        SetCash(100000);
        SetBenchmark(_ => 100m);
        AddData<QrosSyntheticBar>("QROS", Resolution.Daily, TimeZones.Utc);
    }

    public void OnData(QrosSyntheticBar data)
    {
        _rows++;
        _sum += data.Value;
        _last = data.Value;
    }

    public override void OnEndOfAlgorithm()
    {
        if (_rows != 5 || _sum != 510m || _last != 104m)
        {
            throw new InvalidOperationException(
                $"Synthetic input mismatch rows={_rows} sum={_sum} last={_last}");
        }

        SetSummaryStatistic("QROS Rows", _rows.ToString(CultureInfo.InvariantCulture));
        SetSummaryStatistic("QROS Sum", _sum.ToString("0.0000", CultureInfo.InvariantCulture));
        SetSummaryStatistic("QROS Last", _last.ToString("0.0000", CultureInfo.InvariantCulture));
    }
}

public sealed class QrosSyntheticBar : BaseData
{
    public decimal Close { get; set; }

    public override SubscriptionDataSource GetSource(
        SubscriptionDataConfig config, DateTime date, bool isLiveMode)
    {
        if (isLiveMode)
        {
            throw new InvalidOperationException("QROS synthetic fixture is backtest-only");
        }

        var source = Environment.GetEnvironmentVariable("QROS_SYNTHETIC_DATA_FILE");
        if (string.IsNullOrWhiteSpace(source) || !File.Exists(source))
        {
            throw new InvalidOperationException("QROS_SYNTHETIC_DATA_FILE is missing");
        }

        return new SubscriptionDataSource(
            source, SubscriptionTransportMedium.LocalFile, FileFormat.Csv);
    }

    public override BaseData Reader(
        SubscriptionDataConfig config, string line, DateTime date, bool isLiveMode)
    {
        var fields = line.Split(',');
        if (fields.Length != 2)
        {
            throw new FormatException("Synthetic row must have date,close");
        }

        var time = DateTime.ParseExact(
            fields[0], "yyyyMMdd", CultureInfo.InvariantCulture, DateTimeStyles.None);
        var close = decimal.Parse(fields[1], CultureInfo.InvariantCulture);
        if (close <= 0)
        {
            throw new FormatException("Synthetic close must be positive");
        }

        return new QrosSyntheticBar
        {
            Symbol = config.Symbol,
            Time = time,
            EndTime = time.AddDays(1),
            Value = close,
            Close = close
        };
    }
}
