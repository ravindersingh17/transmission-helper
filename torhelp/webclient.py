import requests, re, json
from .epinfo import get_episode_dates

class WebC:

    def __init__(self, url):
        self.url = url

    def init_files(self, download_dir, files_info):
        data = {"download_dir": download_dir, "files": []}
        for f in files_info:
            info = {}
            filepath = f["name"].split("/")
            info["filename"] = filepath[-1]
            info["path"] = "/".join(filepath[:-1])
            p = re.compile("S(\d+)E(\d+)", re.IGNORECASE)
            try:
                season, episode_num = p.search(f["name"]).groups()
                is_episode = True
                show_rough = info["filename"][:p.search(info["filename"]).start() - 1].replace(".", " ")
                proper_name = get_episode_dates(show_rough)[0]
                if not proper_name: return False
            except AttributeError:
                season, episode_num = 0, 0
                is_episode = False
                proper_name = re.search("[\s\w\.\-]+", info["path"]).group()
            info["is_episode"] = is_episode
            info["season"] = season
            info["episode_num"] = episode_num
            info["proper_name"] = proper_name
            data["files"].append(info)
        return requests.post(self.url + "/fromtor", json=data).json()

    def update_files(self, files_info):
        data = []
        for f in files_info:
            if f["size"] != f["completed"]: continue #Only send completed files
            info = {}
            filepath = f["name"].split("/")
            info["filename"] = filepath[-1]
            info["path"] = "/".join(filepath[:-1])
            data.append(info)
        r = requests.post(self.url +"/upfiles", json=data).text
        with open("debug.html", "w") as f: f.write(r)
