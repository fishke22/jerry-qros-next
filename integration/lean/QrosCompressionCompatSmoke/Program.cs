using System;
using System.IO;
using System.Linq;
using System.Text;
using Ionic.Zip;
using QuantConnect;

var root = Path.Combine(Path.GetTempPath(), "qros-compression-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(root);
try
{
    var source = Path.Combine(root, "source.zip");
    var saved = Path.Combine(root, "saved.zip");

    if (!Compression.ZipCreateAppendData(source, "a.csv", Encoding.UTF8.GetBytes("alpha\n"), true))
    {
        throw new InvalidOperationException("ZipCreateAppendData failed");
    }

    using (var zip = ZipFile.Read(source))
    {
        if (zip.Count != 1 || zip[0].FileName != "a.csv")
        {
            throw new InvalidOperationException("compat read mismatch");
        }

        using var reader = new StreamReader(zip[0].OpenReader());
        if (reader.ReadToEnd() != "alpha\n")
        {
            throw new InvalidOperationException("compat content mismatch");
        }

        zip.AddEntry("b.csv", Encoding.UTF8.GetBytes("beta\n"));
        zip.Save(saved);
    }

    using (var verify = ZipFile.Read(saved))
    {
        var names = verify.Entries.Select(x => x.FileName).OrderBy(x => x).ToArray();
        if (names.Length != 2 || names[0] != "a.csv" || names[1] != "b.csv")
        {
            throw new InvalidOperationException("compat save mismatch");
        }
    }

    var maliciousZip = Path.Combine(root, "malicious.zip");
    var extractRoot = Path.Combine(root, "extract");
    var escapedPath = Path.Combine(root, "escape.txt");
    Directory.CreateDirectory(extractRoot);
    using (var archive = System.IO.Compression.ZipFile.Open(
        maliciousZip, System.IO.Compression.ZipArchiveMode.Create))
    {
        var entry = archive.CreateEntry("../escape.txt");
        using var writer = new StreamWriter(entry.Open());
        writer.Write("must-not-escape");
    }

    var maliciousAccepted = Compression.Unzip(maliciousZip, extractRoot, true);
    if (maliciousAccepted || File.Exists(escapedPath))
    {
        throw new InvalidOperationException(
            "path traversal archive escaped extraction root");
    }

    Console.WriteLine("QROS compression path traversal regression: PASS");
    Console.WriteLine("QROS compression compatibility smoke: PASS");
}
finally
{
    Directory.Delete(root, recursive: true);
}
