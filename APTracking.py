import urllib.request
from bs4 import BeautifulSoup
class Item:
    def __init__(self, name, anzahl, last_found):
        self.name = name
        self.anzahl = anzahl
        self.last_found = last_found
    def __lt__(self, other):
        pass
url = "https://archipelago.gg/tracker/6BBHpzZ6Tou2WLhAS2O97A/0/16"
open_page = urllib.request.urlopen(url)
soup = BeautifulSoup(open_page, "html.parser")
Tabelle = soup.find("table", id="received-table")
tds = Tabelle.find_all("td")
print(tds)