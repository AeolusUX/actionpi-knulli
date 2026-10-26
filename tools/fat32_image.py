"""Read-only FAT inspection plus explicit bounded file removal helpers."""
import struct
BOOT_RESOURCE_OFFSET=73728*512

class Fat32Editor:
    def __init__(self, file_handle, offset):
        self.f = file_handle
        self.offset = offset
        self.f.seek(offset)
        bpb = self.f.read(512)
        self.bps = struct.unpack_from("<H", bpb, 11)[0]
        self.spc = bpb[13]
        self.reserved = struct.unpack_from("<H", bpb, 14)[0]
        self.fats = bpb[16]
        self.fat_sectors = struct.unpack_from("<I", bpb, 36)[0]
        self.root = struct.unpack_from("<I", bpb, 44)[0]
        self.fat_offset = offset + self.reserved * self.bps
        self.data_offset = offset + (self.reserved + self.fats * self.fat_sectors) * self.bps
        self.cluster_size = self.bps * self.spc

    def next_cluster(self, cluster):
        self.f.seek(self.fat_offset + cluster * 4)
        return struct.unpack("<I", self.f.read(4))[0] & 0x0FFFFFFF

    def chain(self, start):
        seen = set()
        cluster = start
        while 2 <= cluster < 0x0FFFFFF8 and cluster not in seen:
            seen.add(cluster)
            yield cluster
            cluster = self.next_cluster(cluster)

    def cluster_offset(self, cluster):
        return self.data_offset + (cluster - 2) * self.cluster_size

    def entries(self, start):
        lfn = []
        for cluster in self.chain(start):
            base = self.cluster_offset(cluster)
            self.f.seek(base)
            data = self.f.read(self.cluster_size)
            for local in range(0, len(data), 32):
                entry = data[local:local + 32]
                if entry[0] == 0:
                    return
                if entry[0] == 0xE5:
                    lfn = []
                    continue
                attr = entry[11]
                if attr == 0x0F:
                    chars = entry[1:11] + entry[14:26] + entry[28:32]
                    lfn.insert(0, chars.decode("utf-16le", "ignore").rstrip("\uffff\x00"))
                    continue
                short = entry[:8].decode("ascii", "replace").rstrip()
                ext = entry[8:11].decode("ascii", "replace").rstrip()
                name = "".join(lfn) if lfn else short + (("." + ext) if ext else "")
                lfn = []
                child = (struct.unpack_from("<H", entry, 20)[0] << 16) | struct.unpack_from("<H", entry, 26)[0]
                size = struct.unpack_from("<I", entry, 28)[0]
                yield name, attr, child, size, base + local

    def locate(self, path):
        cluster = self.root
        parts = [part for part in path.strip("/").split("/") if part]
        for index, part in enumerate(parts):
            match = next((item for item in self.entries(cluster) if item[0].casefold() == part.casefold()), None)
            if not match:
                raise FileNotFoundError(path)
            if index != len(parts) - 1 and not match[1] & 0x10:
                raise NotADirectoryError(part)
            cluster = match[2]
        return match

    def replace_file(self, path, content):
        name, attr, start, old_size, entry_offset = self.locate(path)
        clusters = list(self.chain(start))
        capacity = len(clusters) * self.cluster_size
        if len(content) > capacity:
            raise RuntimeError(f"replacement for {path} exceeds allocated FAT chain")
        remaining = content + bytes(capacity - len(content))
        for index, cluster in enumerate(clusters):
            begin = index * self.cluster_size
            self.f.seek(self.cluster_offset(cluster))
            self.f.write(remaining[begin:begin + self.cluster_size])
        self.f.seek(entry_offset + 28)
        self.f.write(struct.pack("<I", len(content)))
        print(f"FAT replace {path}: {old_size} -> {len(content)} bytes")

    def remove_file(self, path):
        _, _, _, _, entry_offset = self.locate(path)
        self.f.seek(entry_offset)
        self.f.write(b"\xE5")
        print(f"FAT hide {path}")

    def read_file(self, path):
        _, _, start, size, _ = self.locate(path)
        out = bytearray()
        for cluster in self.chain(start):
            self.f.seek(self.cluster_offset(cluster))
            out.extend(self.f.read(self.cluster_size))
        return bytes(out[:size])

