using System;
using System.IO;
using System.Linq;
using System.Text;
using Ionic.Zip;
using QuantConnect;

var root=Path.Combine(Path.GetTempPath(),"qros-compression-regression-"+Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(root);
try
{
    var zip=Path.Combine(root,"regression.zip");
    if(!Compression.ZipCreateAppendData(zip,"a.txt","alpha",false)) throw new Exception("initial append failed");
    if(Compression.ZipCreateAppendData(zip,"a.txt","ignored",false)) throw new Exception("duplicate append should fail");
    if(!Compression.ZipCreateAppendData(zip,"a.txt","replaced",true)) throw new Exception("override failed");
    if(!Compression.ZipCreateAppendData(zip,"b.txt","beta",false)) throw new Exception("second append failed");

    var names=Compression.GetZipEntryFileNames(zip).OrderBy(x=>x).ToArray();
    if(names.Length!=2 || names[0]!="a.txt" || names[1]!="b.txt") throw new Exception("entry names mismatch");

    using(var z=ZipFile.Read(zip))
    {
        if(z.Count!=2) throw new Exception("ZipFile count mismatch");
        if(z["a.txt"].UncompressedSize!=8) throw new Exception("size mismatch");
        using var reader=new StreamReader(z["a.txt"].OpenReader());
        if(reader.ReadToEnd()!="replaced") throw new Exception("stream-backed read mismatch");
    }

    var unicodeZip=Path.Combine(root,"unicode.zip");
    var json="{\"Ł\":\"unicode\"}";
    var bytes=Encoding.UTF8.GetBytes(json);
    var zipped=Compression.ZipBytes(bytes,"entry.json");
    var decompressed=Compression.UnzipData(zipped,Encoding.UTF8);
    if(decompressed.Single().Value!=json) throw new Exception("encoding regression");

    var largeZip=Path.Combine(root,"large.zip");
    using(var fs=new FileStream(largeZip,FileMode.Create,FileAccess.Write))
    using(var archive=new System.IO.Compression.ZipArchive(fs,System.IO.Compression.ZipArchiveMode.Create))
    {
        var e=archive.CreateEntry("large.bin",System.IO.Compression.CompressionLevel.Optimal);
        using var s=e.Open();
        var block=new byte[1024*1024];
        for(var i=0;i<24;i++) s.Write(block,0,block.Length);
    }
    using(var z=ZipFile.Read(largeZip))
    {
        if(z[0].UncompressedSize!=24L*1024*1024) throw new Exception("large entry size mismatch");
        using var s=z[0].OpenReader();
        var probe=new byte[4096];
        if(s.Read(probe,0,probe.Length)!=probe.Length) throw new Exception("large entry streaming probe failed");
    }

    Console.WriteLine("QROS Phase 3E targeted compression regression: PASS");
}
finally
{
    Directory.Delete(root,true);
}
