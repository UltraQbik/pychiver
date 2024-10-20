import os


HEADER_FILESIZE: int = 8


class Archive:
    """
    Archive class
    """

    def __init__(self):
        self.files: set[str] = set()

    def put(self, filepath: str) -> None:
        """
        Puts a file into archive
        :param filepath: path to file
        """

        if os.path.isfile(filepath):
            self.files.add(filepath)
        else:
            raise FileNotFoundError(f"Unable to find file at '{filepath}'")

    def pack(self, name: str) -> int:
        """
        Packs archive with the given name.
        :param name: name of the archive
        :return: number of bytes written
        """

        # pack the archive
        with open(name, "wb") as archive:
            archive.write(b'\x00' * HEADER_FILESIZE)  # size of the archive
            for file in self.files:
                # write header
                archive.write(os.path.basename(file).encode("utf-8") + b'\x00')  # write filename
                archive.write(os.path.getsize(file).to_bytes(HEADER_FILESIZE))  # write filesize

                # write file data
                with open(file, "rb") as f:
                    archive.write(f.read())

            # write archive size
            archive_size = archive.tell()
            archive.seek(0)
            archive.write(archive_size.to_bytes(HEADER_FILESIZE))

            # return archive size
            return archive_size

    @staticmethod
    def unpack(filepath: str, unpack_path: str = "") -> None:
        """
        Unpacks archive at given filepath.
        :param filepath: filepath to archive
        :param unpack_path: path where to unpack
        """

        # make unpack path if it doesn't exist
        if not os.path.exists(unpack_path):
            os.makedirs(os.path.dirname(unpack_path+"/" if unpack_path[-1] != "/" else unpack_path))

        # unpack the archive
        with open(filepath, "rb") as archive:
            archive_size = int.from_bytes(archive.read(HEADER_FILESIZE))
            while archive.tell() < archive_size:
                # get filename
                filename = bytearray()
                while (byte := archive.read(1)) != b'\x00':
                    filename += byte

                # get filesize
                filesize = int.from_bytes(archive.read(HEADER_FILESIZE))

                # write file
                with open(os.path.join(unpack_path, filename.decode("utf-8")), "wb") as file:
                    file.write(archive.read(filesize))


def main():
    archive = Archive()
    for path in os.listdir("topack"):
        archive.put(os.path.join("topack", path))
    archive.pack("cool_archive.arch")

    Archive.unpack("cool_archive.arch", "unpacked")


if __name__ == '__main__':
    main()
