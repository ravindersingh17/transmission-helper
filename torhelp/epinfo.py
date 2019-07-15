import requests, json

def get_episode_dates(show_title):
    base_url = "https://api.tvmaze.com/singlesearch/shows"
    params = (("q", show_title), ("embed[]","previousepisode"), ("embed[]", "nextepisode"))
    res = json.loads(requests.get(base_url, params=params).text)
    name = res["name"]
    prevep = None if "previousepisode" not in res["_embedded"] else res["_embedded"]["previousepisode"]["airdate"]
    nextep = None if "nextepisode" not in res["_embedded"] else res["_embedded"]["nextepisode"]["airdate"]
    return(name,prevep, nextep)


