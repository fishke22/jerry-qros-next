using System.IO.Compression;
using System.Reflection;
using Ionic.Zip;

const int UncompressedBytes = 32 * 1024 * 1024;
using var compressed = new MemoryStream();
using (var archive = new ZipArchive(compressed, ZipArchiveMode.Create, leaveOpen: true))
{
    var entry = archive.CreateEntry("high-compression.bin", CompressionLevel.SmallestSize);
    using var output = entry.Open();
    var chunk = new byte[1024 * 1024];
    for (var i = 0; i < 32; i++)
    {
        output.Write(chunk);
    }
}
var compressedBytes = compressed.Length;
compressed.Position = 0;
using var zip = ZipFile.Read(compressed);
var first = zip[0];
var field = typeof(Ionic.Zip.ZipEntry).GetField("_content", BindingFlags.Instance | BindingFlags.NonPublic)
    ?? throw new InvalidOperationException("research bridge _content field not found");
var retained = field.GetValue(first) as byte[]
    ?? throw new InvalidOperationException("research bridge did not retain byte[] content");
if (retained.Length != UncompressedBytes)
{
    throw new InvalidOperationException($"unexpected retained bytes {retained.Length}");
}
if (compressedBytes >= UncompressedBytes / 8)
{
    throw new InvalidOperationException($"probe input is not sufficiently compressed: {compressedBytes}");
}
Console.WriteLine($"QROS compression resource model: FULL_ENTRY_BUFFERING CONFIRMED retained={retained.Length} compressed={compressedBytes}");
Console.WriteLine("QROS Phase 3E resource promotion condition: FAIL_UNBOUNDED_BUFFERING");
