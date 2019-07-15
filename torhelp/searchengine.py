from . import x1337, piratebay

class SearchEngine:

    def __init__(self, engine):
        if engine.startswith("pirate"):
            self.getsearches = piratebay.getsearches
            self.gettorrent = piratebay.gettorrent
        else:
            self.getsearches = x1337.getsearches
            self.gettorrent = x1337.gettorrent
