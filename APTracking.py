from ftplib import FTP_TLS
import urllib.request
from bs4 import BeautifulSoup
def einzeltracker_drurchgehen(link:str):
    neu = {}
    seite = urllib.request.urlopen(link)
    soup = BeautifulSoup(seite, "html.parser")
    erster_link = soup.find("a")
    if erster_link.contents[0] == "Switch To Generic Tracker":
        seite = urllib.request.urlopen(link.replace("tracker","generic_tracker"))
        soup = BeautifulSoup(seite, "html.parser")
    Tabelle = soup.find("table", id="received-table")
    tds = Tabelle.find_all("td")
    for i in range(len(tds)):
        if i % 3 == 0:
            name = tds[i].contents[0]
        elif i % 3 == 1:
            neu[name] = tds[i].contents[0]
        else:
            pass
    return neu

###############################################################################################

try:
    config_name = ""
    config_tracker = ""
    ftpurl=""
    ftpuser=""
    ftppw=""
    with open("APTracking.config", "r") as config_datei:
        for config_zeile in config_datei.readlines():
            if config_zeile.startswith("#"):
                continue
            elif config_zeile.count("=") == 1:
                zeilen_teile = config_zeile.split("=")
                if zeilen_teile[0].upper() == "NAME":
                    config_name = zeilen_teile[1].strip()
                elif zeilen_teile[0].upper() == "TRACKER":
                    config_tracker = zeilen_teile[1].strip()
                elif zeilen_teile[0].upper() == "FTPURL":
                    ftpurl = zeilen_teile[1].strip()
                elif zeilen_teile[0].upper() == "FTPUSER":
                    ftpuser = zeilen_teile[1].strip()
                elif zeilen_teile[0].upper() == "FTPPW":
                    ftppw = zeilen_teile[1].strip() 
                else:
                    raise NameError(f"Ungültiger Parameter in der Config: {zeilen_teile[0]}", name=zeilen_teile[0])
            else:
                raise ValueError(f"Ungültiges Format der Zeile in der config Datei: {config_zeile}")
    # print(f"name = {name}")
    # print(f"tracker = {tracker}")
    link = f"https://archipelago.gg/tracker/{config_tracker}"
    seite = urllib.request.urlopen(link)
    soup = BeautifulSoup(seite, "html.parser")
    aptracker = soup.find("table", id="checks-table")
    tds = aptracker.find_all("td")
    for i in range(len(tds)-7):
        # print(f"{i % 7}: {aptracker_tds[i]}")
        if i % 7 == 0:
            link = f'https://archipelago.gg{tds[i].find("a")["href"]}'
        elif i % 7 == 1:
            name = str(tds[i].contents[0])
        elif i % 7 == 2 and name.count(config_name) > 0:
            game = str(tds[i].contents[0])
            # print(f"{name}, Spiel {game}: {link}")
            neu = einzeltracker_drurchgehen(link)
            print(neu)
            with FTP_TLS(ftpurl,ftpuser,ftppw,) as ftp_connection:
                print(ftp_connection.pwd())
        else:
            pass
except Exception as e:
    print(e)