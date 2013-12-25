import os
import re
import struct

class MovieFile:

    nocd = 0
    supported_filetypes = ('avi','mpeg','mpg','mkv','wmv','mp4')

    def __init__(self,filepath):
        if not os.path.exists(filepath):
            raise Exception("File %s doesn't exist" % filepath)
        if not filepath.endswith(self.supported_filetypes):
            raise Exception("File doesn't seem to be a video file") # FIXME
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.dirname = os.path.dirname(filepath)
        self.nocd = self._nocd()

    def _nocd(self):
        """
        Check filepath to see if move is single file or multiple
        """
        if not re.match(self.filepath, 'CD\d+$'):
            self.nocd = 1
        else:
            for f in os.listdir(self.dirname):
                if f.endswith(self.supported_filetypes):
                    if re.match(f, 'CD\d+$'):
                        self.nocd += 1

    def _getimdbid(self):
        for f in os.listdir(self.dirname):
            if f.endswith('nfo'):
                with open(os.path.join(self.dirname, f), 'r') as fp:
                    m = re.search("www\.imdb\.com/title/tt(\d+)/", fp.read())
                    if m: return m.group(1)

        return None

    def _hash(self):
        if not self.filepath:
            raise Exception("Can only hash actual movie files")
        try:
            longlongformat = 'q'  # long long
            bytesize = struct.calcsize(longlongformat)

            f = open(self.filepath, "rb")

            filesize = os.path.getsize(self.filepath)
            hash = filesize

            if filesize < 65536 * 2:
               return "SizeError"

            for x in range(65536/bytesize):
                buffer = f.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number


            f.seek(max(0,filesize-65536),0)
            for x in range(65536/bytesize):
                buffer = f.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

            f.close()
            returnedhash =  "%016x" % hash
            return returnedhash
        except(IOError):
            return "IOError"

    def _bytesize(self):
        if not self.filepath:
            raise Exception("Can only get bytesize for actual movie file")

        return str(os.stat(self.filepath)[6])

    def addsub(self, substr, ext="srt"):
        """
        Add a subtitle file to the movie file.

        The name of the file is the same as the name of the movie and if the
        file already exists an identifier is added just before the extension.

        eg:
        foo.avi
        foo.srt
        foo.1.srt
        """
        basename = "%s/%s" % (self.dirname,
            os.path.splitext(self.filename)[0])

        fname = "%s.%s" % (basename, ext)
        if os.path.exists(fname):
            inc = 1
            while os.path.exists("%s.%s.%s" % (basename, inc, ext)):
                inc += 1

            fname = "%s.%s.%s" % (basename, inc, ext)
        with open(fname, 'w') as f:
            f.write(substr)

        return fname
