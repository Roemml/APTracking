import os
from ftplib import FTP_TLS
import urllib.request
from bs4 import BeautifulSoup
import Roemdules
import Roemdules.gui
def get_input_from_file(file_name):
    config_name = ""
    config_tracker = ""
    ftpurl=""
    ftpuser=""
    ftppw=""
    with open(file_name, "r") as config_datei:
        for config_zeile in config_datei.readlines():
            if config_zeile.startswith("#"):
                continue
            elif config_zeile.count("=") == 1:
                argument, wert = config_zeile.split("=")
                if argument.upper() == "NAME":
                    config_name = wert.strip()
                elif argument.upper() == "TRACKER":
                    config_tracker = wert.strip()
                elif argument.upper() == "FTPURL":
                    ftpurl = wert.strip()
                elif argument.upper() == "FTPUSER":
                    ftpuser = wert.strip()
                elif argument.upper() == "FTPPW":
                    ftppw = wert.strip() 
                else:
                    raise NameError(f"Ungültiger Parameter in der Config: {argument}", name=argument)
            else:
                raise ValueError(f"Ungültiges Format der Zeile in der config Datei: {config_zeile}")
    return (config_name, config_tracker, ftpurl, ftpuser, ftppw)
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
def FTP_read(ftpurl,ftpuser,ftppw,file_name,file):
    with FTP_TLS(ftpurl,ftpuser,ftppw) as ftp_connection:
        try:
            ftp_connection.retrbinary(f"RETR {file_name}", file.write)
            return True
        except Exception as e:
            return False
def FTP_write(ftpurl,ftpuser,ftppw,file_name,file):
    with FTP_TLS(ftpurl,ftpuser,ftppw) as ftp_connection:
        try:
            ftp_connection.storlines(f"STOR {file_name}", file)
            return True
        except Exception as e:
            return False
###############################################################################################

try:
    fenster = Roemdules.gui.erstelle_Fenster(
        {"type":"label", "text":"Spieler (Teil)Name:", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":20, "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"AP Tracker ID", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":20, "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"FTP/DB Name:", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":20, "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"FTP/DB Passwort:", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":20, "align":Roemdules.gui.ALIGN_LEFT}
        # ,{"type":"button", "text":"Start", "command":"startSpiel(fenster)", "width":5, "height":1, "align":Roemdules.gui.ALIGN_CENTER}
        ,fenster_name = "Start"#, protocols = (("WM_DELETE_WINDOW", "start_fenster_schliessen(fenster,game_state)"),)
        #,context = {'game_state': game_state, 'start_fenster_schliessen': start_fenster_schliessen, 'startSpiel': startSpiel}
        )
    fenster.mainloop()
    config_name, config_tracker, ftpurl, ftpuser, ftppw = get_input_from_file("APTracking.config")
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
            file_name = f"{config_tracker}_{name}.txt"
        elif i % 7 == 2 and name.count(config_name) > 0:
            game = str(tds[i].contents[0])
            # print(f"{name}, Spiel {game}: {link}")
            neu = einzeltracker_drurchgehen(link)
            print(f"game: {game}")
            with open(f"{config_tracker}_{name}.txt", "wb") as file_alt:
                FTP_read(ftpurl,ftpuser,ftppw,file_name,file_alt)
            alt = {}
            with open(file_name, 'r') as file_alt:
                alt_lines = file_alt.readlines()
                for line in alt_lines:
                    item, anzahl = line.split("=")
                    alt[item] = anzahl
            with open(file_name, 'w') as file_neu:
                for item, anzahl in neu.items():
                    file_neu.write(f"{item}={anzahl}\n")
                    if (item in alt):
                        if anzahl > alt[item]:
                            print(f"{item}: {anzahl - alt[item]}")
                    else:
                        print(f"{item}: {anzahl}")
                print("")
            with open(file_name, 'rb') as file_neu:
                FTP_write(ftpurl,ftpuser,ftppw,file_name,file_neu)
            os.remove(file_name)
        else:   
            pass
except Exception as e:
    print(f"{e.__class__}: {e}")