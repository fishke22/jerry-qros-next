from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "external" / "lean"

MESSAGING_OLD = '<PackageReference Include="NetMQ" Version="4.0.1.6" />'
MESSAGING_NEW = '<PackageReference Include="NetMQ" Version="4.0.4.3" />'
DOTNETZIP_LINE = '    <PackageReference Include="DotNetZip" Version="1.16.0" />\n'

RUNTIME_COMPRESSION_BRIDGE = """// QROS RESEARCH-ONLY STREAM-BACKED COMPATIBILITY BRIDGE.
// Not an upstream LEAN source file. Do not promote without architecture review.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;

namespace Ionic.Zip
{
    public enum Zip64Option
    {
        Default = 0,
        Always = 1
    }

    public class ZipException : Exception
    {
        public ZipException() { }
        public ZipException(string message) : base(message) { }
        public ZipException(string message, Exception inner) : base(message, inner) { }
    }

    public sealed class ZipEntry
    {
        private readonly ZipArchiveEntry _sourceEntry;
        private readonly byte[] _content;
        private readonly long _size;

        internal ZipEntry(ZipArchiveEntry sourceEntry)
        {
            _sourceEntry = sourceEntry ?? throw new ArgumentNullException(nameof(sourceEntry));
            FileName = sourceEntry.FullName;
            _size = sourceEntry.Length;
        }

        internal ZipEntry(string fileName, long size)
        {
            FileName = fileName;
            _size = size;
        }

        public ZipEntry(string fileName)
            : this(fileName, Array.Empty<byte>())
        {
        }

        internal ZipEntry(string fileName, byte[] content)
        {
            FileName = fileName;
            _content = content ?? Array.Empty<byte>();
            _size = _content.LongLength;
        }

        public string FileName { get; }
        public string Name => FileName;
        public long UncompressedSize => _size;
        public long Size => _size;

        public Stream OpenReader()
        {
            if (_sourceEntry != null)
            {
                return _sourceEntry.Open();
            }
            if (_content != null)
            {
                return new MemoryStream(_content, writable: false);
            }
            throw new InvalidOperationException("ZipEntry has no readable backing stream");
        }

        public void Extract(Stream target)
        {
            using var source = OpenReader();
            source.CopyTo(target);
        }

        internal void CopyTo(Stream target)
        {
            using var source = OpenReader();
            source.CopyTo(target);
        }
    }

    public sealed class ZipInputStream : Stream
    {
        private readonly Stream _source;
        private readonly bool _ownsSource;
        private readonly ZipArchive _archive;
        private readonly IEnumerator<ZipArchiveEntry> _entries;
        private Stream _currentStream;

        public ZipInputStream(string path)
        {
            _source = File.OpenRead(path);
            _ownsSource = true;
            _archive = new ZipArchive(_source, ZipArchiveMode.Read, leaveOpen: true);
            _entries = _archive.Entries.GetEnumerator();
        }

        public ZipInputStream(Stream source)
        {
            _source = source ?? throw new ArgumentNullException(nameof(source));
            _archive = new ZipArchive(_source, ZipArchiveMode.Read, leaveOpen: true);
            _entries = _archive.Entries.GetEnumerator();
        }

        public ZipEntry GetNextEntry()
        {
            _currentStream?.Dispose();
            _currentStream = null;
            if (!_entries.MoveNext())
            {
                return null;
            }

            var current = _entries.Current;
            _currentStream = current.Open();
            return new ZipEntry(current.FullName, current.Length);
        }

        public override bool CanRead => _currentStream?.CanRead ?? false;
        public override bool CanSeek => false;
        public override bool CanWrite => false;
        public override long Length => _currentStream?.Length ?? 0;
        public override long Position
        {
            get => _currentStream?.Position ?? 0;
            set => throw new NotSupportedException();
        }

        public override void Flush() { }
        public override int Read(byte[] buffer, int offset, int count)
            => _currentStream?.Read(buffer, offset, count) ?? 0;
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => throw new NotSupportedException();

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _currentStream?.Dispose();
                _entries.Dispose();
                _archive.Dispose();
                if (_ownsSource)
                {
                    _source.Dispose();
                }
            }
            base.Dispose(disposing);
        }
    }

    public sealed class ZipFile : IEnumerable<ZipEntry>, IDisposable
    {
        private readonly List<ZipEntry> _entries = new();
        private Stream _sourceStream;
        private ZipArchive _sourceArchive;
        private bool _ownsSource;

        public ZipFile(string path)
        {
            if (File.Exists(path))
            {
                _sourceStream = File.OpenRead(path);
                _ownsSource = true;
                LoadSourceArchive();
            }
        }

        private ZipFile(Stream stream)
        {
            _sourceStream = stream ?? throw new ArgumentNullException(nameof(stream));
            LoadSourceArchive();
        }

        public static ZipFile Read(string path)
        {
            try
            {
                return new ZipFile(path);
            }
            catch (Exception exception) when (exception is InvalidDataException || exception is IOException)
            {
                throw new ZipException($"Cannot read '{path}' as a zip file", exception);
            }
        }

        public static ZipFile Read(Stream stream)
        {
            try
            {
                return new ZipFile(stream);
            }
            catch (Exception exception) when (exception is InvalidDataException || exception is IOException)
            {
                throw new ZipException("Cannot read stream as a zip file", exception);
            }
        }

        public Zip64Option UseZip64WhenSaving { get; set; }
        public IReadOnlyList<ZipEntry> Entries => _entries;
        public IEnumerable<string> EntryFileNames => _entries.Select(x => x.FileName).ToArray();
        public int Count => _entries.Count;
        public ZipEntry this[int index] => _entries[index];
        public ZipEntry this[string fileName] => _entries.FirstOrDefault(
            x => string.Equals(x.FileName, fileName, StringComparison.OrdinalIgnoreCase));

        public bool ContainsEntry(string fileName) => this[fileName] != null;

        public void RemoveEntry(string fileName)
        {
            var entry = this[fileName];
            if (entry != null)
            {
                _entries.Remove(entry);
            }
        }

        public ZipEntry AddEntry(string fileName, byte[] content)
        {
            var entry = new ZipEntry(fileName, content);
            _entries.Add(entry);
            return entry;
        }

        public void Save(string path)
        {
            using var output = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.None);
            using var archive = new ZipArchive(output, ZipArchiveMode.Create, leaveOpen: false);
            foreach (var entry in _entries)
            {
                var archiveEntry = archive.CreateEntry(entry.FileName, CompressionLevel.Optimal);
                using var target = archiveEntry.Open();
                entry.CopyTo(target);
            }
        }

        public IEnumerator<ZipEntry> GetEnumerator() => _entries.GetEnumerator();
        IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

        public void Dispose()
        {
            _sourceArchive?.Dispose();
            _sourceArchive = null;
            if (_ownsSource)
            {
                _sourceStream?.Dispose();
            }
            _sourceStream = null;
        }

        private void LoadSourceArchive()
        {
            _sourceArchive = new ZipArchive(_sourceStream, ZipArchiveMode.Read, leaveOpen: true);
            foreach (var entry in _sourceArchive.Entries)
            {
                _entries.Add(new ZipEntry(entry));
            }
        }
    }
}

namespace Ionic.BZip2
{
    public sealed class BZip2InputStream : Stream
    {
        private readonly ICSharpCode.SharpZipLib.BZip2.BZip2InputStream _inner;
        public BZip2InputStream(Stream source)
        {
            _inner = new ICSharpCode.SharpZipLib.BZip2.BZip2InputStream(source);
        }
        public override bool CanRead => _inner.CanRead;
        public override bool CanSeek => _inner.CanSeek;
        public override bool CanWrite => false;
        public override long Length => _inner.Length;
        public override long Position { get => _inner.Position; set => _inner.Position = value; }
        public override void Flush() => _inner.Flush();
        public override int Read(byte[] buffer, int offset, int count) => _inner.Read(buffer, offset, count);
        public override long Seek(long offset, SeekOrigin origin) => _inner.Seek(offset, origin);
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => throw new NotSupportedException();
        protected override void Dispose(bool disposing)
        {
            if (disposing) _inner.Dispose();
            base.Dispose(disposing);
        }
    }
}

namespace Ionic.Zlib
{
    public enum CompressionMode
    {
        Compress = 0,
        Decompress = 1
    }

    public sealed class GZipStream : Stream
    {
        private readonly System.IO.Compression.GZipStream _inner;
        public GZipStream(Stream stream, CompressionMode mode)
        {
            _inner = new System.IO.Compression.GZipStream(
                stream,
                mode == CompressionMode.Decompress
                    ? System.IO.Compression.CompressionMode.Decompress
                    : System.IO.Compression.CompressionMode.Compress);
        }
        public override bool CanRead => _inner.CanRead;
        public override bool CanSeek => _inner.CanSeek;
        public override bool CanWrite => _inner.CanWrite;
        public override long Length => _inner.Length;
        public override long Position { get => _inner.Position; set => _inner.Position = value; }
        public override void Flush() => _inner.Flush();
        public override int Read(byte[] buffer, int offset, int count) => _inner.Read(buffer, offset, count);
        public override long Seek(long offset, SeekOrigin origin) => _inner.Seek(offset, origin);
        public override void SetLength(long value) => _inner.SetLength(value);
        public override void Write(byte[] buffer, int offset, int count) => _inner.Write(buffer, offset, count);
        protected override void Dispose(bool disposing)
        {
            if (disposing) _inner.Dispose();
            base.Dispose(disposing);
        }
    }

    public class ZlibException : Exception
    {
        public ZlibException() { }
        public ZlibException(string message) : base(message) { }
        public ZlibException(string message, Exception inner) : base(message, inner) { }
    }
}
"""


def _replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if new and new in text:
        raise RuntimeError(f"candidate already applied to {path}")
    if text.count(old) != 1:
        raise RuntimeError(f"expected exact source text not found once in {path}")
    path.write_text(text.replace(old, new), encoding="utf-8")


PATH_TRAVERSAL_OLD = """                else
                {
                    using (var archive = new ZipArchive(File.OpenRead(zip)))
                    {
                        foreach (var file in archive.Entries)
                        {
                            // skip directories
                            if (string.IsNullOrEmpty(file.Name)) continue;
                            var filepath = Path.Combine(directory, file.FullName);
                            if (IsLinux) filepath = filepath.Replace(@"\\", "/");
                            var outputFile = new FileInfo(filepath);
                            if (!outputFile.Directory.Exists)
                            {
                                outputFile.Directory.Create();
                            }
                            file.ExtractToFile(outputFile.FullName, true);
                        }
                    }
                }
"""

UNZIP_TO_FOLDER_OLD = """                    // Manipulate the output filename here as desired.
                    var fullZipToPath = Path.Combine(outFolder, zipEntry.FullName);

                    var targetFile = new FileInfo(fullZipToPath);
                    if (targetFile.Directory != null && !targetFile.Directory.Exists)
                    {
                        targetFile.Directory.Create();
                    }

                    //Save the file name for later:
                    files.Add(fullZipToPath);

                    //Copy the data in buffer chunks
                    using var entryStream = zipEntry.Open();
                    using var streamWriter = File.Create(fullZipToPath);
                    entryStream.CopyTo(streamWriter);
"""

UNZIP_TO_FOLDER_NEW = """                    var extractionRoot = Path.GetFullPath(outFolder);
                    if (!extractionRoot.EndsWith(Path.DirectorySeparatorChar.ToString(), StringComparison.Ordinal))
                    {
                        extractionRoot += Path.DirectorySeparatorChar;
                    }

                    var entryPath = IsLinux ? zipEntry.FullName.Replace(@"\\", "/") : zipEntry.FullName;
                    var fullZipToPath = Path.GetFullPath(Path.Combine(extractionRoot, entryPath));
                    if (!fullZipToPath.StartsWith(extractionRoot, StringComparison.Ordinal))
                    {
                        throw new IOException($"Archive entry '{zipEntry.FullName}' would extract outside the destination directory.");
                    }

                    var targetFile = new FileInfo(fullZipToPath);
                    if (targetFile.Directory != null && !targetFile.Directory.Exists)
                    {
                        targetFile.Directory.Create();
                    }

                    //Save the file name for later:
                    files.Add(fullZipToPath);

                    //Copy the data in buffer chunks
                    using var entryStream = zipEntry.Open();
                    using var streamWriter = File.Create(fullZipToPath);
                    entryStream.CopyTo(streamWriter);
"""

PATH_TRAVERSAL_NEW = """                else
                {
                    var extractionRoot = Path.GetFullPath(directory);
                    if (!extractionRoot.EndsWith(Path.DirectorySeparatorChar.ToString(), StringComparison.Ordinal))
                    {
                        extractionRoot += Path.DirectorySeparatorChar;
                    }

                    using (var archive = new ZipArchive(File.OpenRead(zip)))
                    {
                        foreach (var file in archive.Entries)
                        {
                            // skip directories
                            if (string.IsNullOrEmpty(file.Name)) continue;
                            var entryPath = IsLinux ? file.FullName.Replace(@"\\", "/") : file.FullName;
                            var filepath = Path.GetFullPath(Path.Combine(extractionRoot, entryPath));
                            if (!filepath.StartsWith(extractionRoot, StringComparison.Ordinal))
                            {
                                throw new IOException($"Archive entry '{file.FullName}' would extract outside the destination directory.");
                            }

                            var outputFile = new FileInfo(filepath);
                            if (!outputFile.Directory.Exists)
                            {
                                outputFile.Directory.Create();
                            }
                            file.ExtractToFile(outputFile.FullName, true);
                        }
                    }
                }
"""

def apply(candidate: str) -> list[Path]:
    if candidate == "messaging-netmq-4.0.4.3":
        path = LEAN / "Messaging" / "QuantConnect.Messaging.csproj"
        _replace_once(path, MESSAGING_OLD, MESSAGING_NEW)
        return [path]

    if candidate == "compression-path-traversal-hardening":
        path = LEAN / "Compression" / "Compression.cs"
        _replace_once(path, PATH_TRAVERSAL_OLD, PATH_TRAVERSAL_NEW)
        _replace_once(path, UNZIP_TO_FOLDER_OLD, UNZIP_TO_FOLDER_NEW)
        return [path]

    if candidate == "compression-system-io-bridge":
        project = LEAN / "Compression" / "QuantConnect.Compression.csproj"
        bridge_path = LEAN / "Compression" / "QrosRuntimeCompressionCompat.cs"
        if bridge_path.exists():
            raise RuntimeError("compression compatibility bridge already exists")
        _replace_once(project, DOTNETZIP_LINE, "")
        bridge_path.write_text(RUNTIME_COMPRESSION_BRIDGE, encoding="utf-8")
        return [project, bridge_path]

    raise KeyError(candidate)


CANDIDATES = {
    "messaging-netmq-4.0.4.3",
    "compression-system-io-bridge",
    "compression-path-traversal-hardening",
}
