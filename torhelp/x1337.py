import re
from bs4 import BeautifulSoup as BS
import requests

def getsearches(search):
    SITE = 'https://www.1377x.to'
    results = []

    rep = lambda x, y: x + y if len(y) == 2 else x + "0" + y
    match = re.search("(\d{1,2})-(\d{1,2})", search)
    if match: search = re.sub("(\d{1,2})-(\d{1,2})", rep("S", match.group(1)) + rep("E", match.group(2)), search)

    response = requests.get(SITE+'/search/%s/1/' % (search.replace(" ", "%20"))).text

    soup = BS(response, 'html.parser')
    tors = [(x["href"], x.text) for x in soup.find_all("a", {"href": re.compile("^/torrent/\d+/.+/")})]
    seeds = [ x.text for x in soup.find_all("td", {"class", "coll-2 seeds"})]
    leeches = [ x.text for x in soup.find_all("td", {"class", "coll-3 leeches"})]
    sizedivs = soup.find_all("td", {"class", re.compile("^coll-4 size.*")})
    for x in sizedivs: x.find("span").extract()
    sizes = [ x.text for x in sizedivs ]


    for i in range(len(tors)):
        yield {
                'text': tors[i][1],
                'size': sizes[i],
                'seeders': (seeds[i], leeches[i]),
                'link': SITE + tors[i][0]
                }

def gettorrent(link):
    response = requests.get(link).text
    soup = BS(response, 'html.parser')
    return soup.find('a', {'href': re.compile('^magnet:.+')})['href']
