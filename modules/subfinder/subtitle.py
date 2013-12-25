import os
import xmlrpclib
import base64
import cStringIO
import gzip
from movie import MovieFile

def pprint(data, index=False):
    """
    Format/print subtitle results
    """
    seen = set()
    if not data:
        return
    for index, line in enumerate(data):
        print "%2s. %30s [%s]\t%4s\t%10s" % (index,
            line['MovieReleaseName'] or line['MovieName'],
            line['SubLanguageID'], line['SubRating'],
            line['SubDownloadsCnt'])

class OSService():
    """
    xmlrpc agent for querying OpenSubtitles
    url: http://api.opensubtitles.org/xml-rpc
    """

    subs = []

    def __init__(self):
        self.client = xmlrpclib.ServerProxy("http://api.opensubtitles.org/xml-rpc",
                allow_none=True)
        reply = self.client.LogIn("","","eng", "OS Test User Agent")
        if reply['status'] != "200 OK":
            raise Exception("Failed to connect: %s" %reply['status'])
        self.token = reply['token']

    def _searchby_hash(self, movie, language="eng"):
        return self.client.SearchSubtitles(self.token,
                [{'sublanguageid':language,
                  'moviehash': movie._hash(),
                  'moviebytesize': movie._bytesize()}])['data'] or []

    def _searchby_imdbid(self, movie, language="eng"):
        if movie._getimdbid() == None: return []
        return self.client.SearchSubtitles(self.token,
                [{'sublanguageid':language,
                  'imdbid': movie._getimdbid()}])['data'] or []

    def _searchby_tag(self, movie, language="eng"):
        return self.client.SearchSubtitles(self.token,
                [{'sublanguageid':language,
                  'tag': movie.filename}])['data'] or []

    def _searchby_query(self, movie, language="eng"):
        return self.client.SearchSubtitles(self.token,
                [{'sublanguageid':language,
                  'moviehash': movie._hash(),
                  'moviebytesize': movie._bytesize()}])['data'] or []

    def search(self, movie, language="eng"):
        self.subs = []

        self.subs.extend(filter(lambda s: s["IDSubtitle"] not in [m["IDSubtitle"] for m in self.subs],
            self._searchby_imdbid(movie, language)))
        self.subs.extend(filter(lambda s: s["IDSubtitle"] not in [m["IDSubtitle"] for m in self.subs],
            self._searchby_query(movie, language)))
        self.subs.extend(filter(lambda s: s["IDSubtitle"] not in [m["IDSubtitle"] for m in self.subs],
            self._searchby_tag(movie, language)))
        self.subs.extend(filter(lambda s: s["IDSubtitle"] not in [m["IDSubtitle"] for m in self.subs],
            self._searchby_hash(movie, language)))

        return self.subs

    def sort(self, keys=["SubRating", "SubDownloadsCnt"]):
        #FIXME: to use keys from args
        self.subs = sorted(self.subs, key=lambda k:
            (float(k['SubRating']), int(k['SubDownloadsCnt'])), reverse=True)
        return self.subs

    def fetch(self, idsub):
        """
        Fetch subs from IDSubtitleFile

        Returns a string with the contents of the file
        """
        srt = self.client.DownloadSubtitles(self.token, [idsub])['data'][0]['data']
        return gzip.GzipFile(fileobj=cStringIO.StringIO(srt.decode("base64"))).read()

    def get(self, movie, language="eng", interactive=False, allsubs=False):
        valid = False
        self.search(movie, language)
        self.sort()
        if not self.subs:
            raise Exception("No subtitles found")
        if interactive:
            pprint(self.subs)
            while not valid:
                sid = raw_input("Select subtitle: [0] ")
                if not sid: sid = 0
                try:
                    if int(sid) in range(0, len(self.subs)):
                        valid = True
                    else:
                        raise
                except Exception:
                    print "Invalid selection"
                    continue
        else:
            sid = 0

        subid = self.subs[int(sid)]["IDSubtitleFile"]
        subformat = self.subs[int(sid)]["SubFormat"]
        movie.addsub(self.fetch(subid))

        # if allsubs is True, get all remaining files as well
        if allsubs:
            for i,s in enumerate(self.subs):
                if i == sid: continue

            subid = self.subs[i]["IDSubtitleFile"]
            subformat = self.subs[i]["SubFormat"]
            movie.addsub(self.fetch(i))

    def upload():
        """
        To be implemented
        """
        pass
