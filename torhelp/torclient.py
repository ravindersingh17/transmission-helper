from transmissionrpc import Client
import time, re

class TorC:
    MANAGE_ACTION_INIT = 1
    MANAGE_ACTION_CLEAN = 2

    TOR_TYPE_SINGLE = 1
    TOR_TYPE_SERIES = 2
 
    Videos = ["mp4", "mkv", "avi", "mpeg", "mpg", "mov", "mov", "wmv"]

    def __init__(self, user, password):
        #TODO: host/port/url
        self.client = Client(user=user, password=password)
        self.torrent_props = {}
        for t in self.client.get_torrents():
            self.sort_by_episodes(t)

    def get_files(self, torrent = None):
        if not torrent:
            ret = []
            for t, tinfo in self.client.get_files().items():
                for fid, finfo in tinfo.items():
                    if finfo["name"].split(".")[-1] in TorC.Videos:
                        ret.append(finfo)
            return ret
        return [x for x in list(torrent.files().values()) if x["name"].split(".")[-1] in TorC.Videos ]

    def download_dir(self):
        return self.client.session.download_dir

    def add_magnet(self, magnet):
        torrent = self.client.add_torrent(magnet)
        while not torrent.files():
            time.sleep(.1)
            torrent.update()
        torrent.uploadLimit = 20
        torrent.stop()
        torrent.update()
        self.manage_files(torrent, TorC.MANAGE_ACTION_INIT)

        return torrent

    def status(self):
        ret = []
        for t in self.client.get_torrents():
            t.update()
            tor_data = [t.name, float(t.rateDownload), []]
            if t.hashString not in self.torrent_props:
                tor_data[2].append({
                            "name": t.name,
                            "completed": float(t.percentDone)*100})
            else:
                files_list = t.files()
                for f in self.torrent_props[t.hashString]["episodes"]:
                    fdict = files_list[f[0]]
                    if fdict["size"] == fdict["completed"] or not fdict["selected"]: continue
                    tor_data[2].append({"name": fdict["name"],
                        "completed": float(100*fdict["completed"])/fdict["size"]}),

            ret.append(tor_data)
        return ret

    def clean(self):
        toremove = []
        for t in self.client.get_torrents():
            t.update()
            if t.hashString not in self.torrent_props:
                if t.status == "seeding": toremove.append(t.id)
            else:
                if not self.start_using_priority(t): toremove.append(t.id)
        if toremove:
            self.client.remove_torrent(toremove)

    def init_torrent_download(self, torrent):
        files_list = torrent.files()
        self.torrent_props[torrent.hashString]  = {}
        #Skip all files:
        skip_files = {torrent.id : {}}
        for idx, f in enumerate(files_list):
            skip_files[torrent.id][idx] = {"selected": False}
        self.client.set_files(skip_files)

        video_files = { k:v for k,v in files_list.items() if v["name"].split(".")[-1].lower() in TorC.Videos }
        if len(video_files) > 1:
            sizesorted_files_list = sorted(video_files.values(), key=lambda x: x["size"], reverse=True)
            if sizesorted_files_list[0]["size"] > 5* sizesorted_files_list[1]["size"]:
                video_files = [sizesorted_files_list[0]]

        self.torrent_props[torrent.hashString]["episodes"] = self.sort_by_episodes(torrent)
        if len(video_files) > 2: #Type is series
            self.sort_by_episodes(torrent)
            self.start_using_priority(torrent)
        else:
            start_files = {}
            for idx,f in video_files.items():
                start_files[torrent.id] = {idx:{"selected": True}}
            self.client.set_files(start_files)




    def start_using_priority(self, torrent, startat=0):
        #TODO startat function
        files_list = torrent.files()
        pos = startat
        f = files_list[self.torrent_props[torrent.hashString]["episodes"][pos][0]]
        while  pos < len(self.torrent_props[torrent.hashString]["episodes"]) and f["size"] == f["completed"]:
            pos += 1
            try:
                f = files_list[self.torrent_props[torrent.hashString]["episodes"][pos][0]]
            except IndexError: pass
        if pos == len(self.torrent_props[torrent.hashString]["episodes"]):
            return False
        mod_files = {torrent.id:{self.torrent_props[torrent.hashString]["episodes"][pos][0]:{"selected": True, "priority": "high"}}}

        if pos < len(self.torrent_props[torrent.hashString]["episodes"]) - 1:
            mod_files[torrent.id][self.torrent_props[torrent.hashString]["episodes"][pos+1][0]] = {"priority":"normal", "selected": True}
        self.client.set_files(mod_files)
        return True

    def manage_files(self, torrent, action):
        files_list = torrent.files()
        if action == TorC.MANAGE_ACTION_INIT:
            self.init_torrent_download(torrent)

    def sort_by_episodes(self, torrent):
        files_list = torrent.files()
        video_files = { k:v for k,v in files_list.items() if v["name"].split(".")[-1].lower() in TorC.Videos }
        p = re.compile("S\d+E\d+", re.IGNORECASE)
        episodes = { re.search(p, v["name"]).group().upper(): (k, v["name"]) for k,v in video_files.items()}
        self.torrent_props[torrent.hashString]= {"episodes": [y[1] for y in sorted(episodes.items(), key = lambda x: x[0])]}

    def start_all(self):
        for t in self.client.get_torrents(): t.start()

    def stop_all(self):
        for t in self.client.get_torrents(): t.stop()
