import tkinter as tk
import os
import sys
from ftplib import FTP_TLS
import mysql.connector
import urllib.request
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from cryptography.fernet import Fernet
#import Roemdules
import Roemdules.gui
class Config():
    def __init__(self):
        self.modus:tk.StringVar = ""
        self.name = ""
        self.tracker = ""
        self.url = ""
        self.user = ""
        self.passwort = ""
        self.dbname = ""
def beenden():
    # fenster.destroy()
    sys.exit("Exit program") 
def get_config_from_window(fenster:tk.Tk, config: Config):
    for child in fenster.children.values():
        if("name" in child.__dict__): 
            if child.name == "Name":
                config.name = child.get()
            elif child.name == "Tracker":
                config.tracker = child.get()
            elif child.name == "Url":
                config.url = child.get()
            elif child.name == "User":
                config.user = child.get()
            elif child.name == "Passwort":
                config.passwort = child.get()
            elif child.name == "DBName":
                config.dbname = child.get()
    fenster.destroy()
def get_config_from_file(file_name: str, config: Config):
    load_dotenv(file_name)
    key = os.getenv("FKEY").encode()
    fernet = Fernet(key)
    def fernet_decrypt(encrypted):
        return fernet.decrypt(encrypted.encode()).decode()
    if config.name == "": config.name = os.getenv("APT_name")
    if config.tracker == "": config.tracker = os.getenv("APT_tracker")
    if config.modus == "FTP":
        if config.url == "":  config.url = fernet_decrypt(os.getenv("APT_FTPURL"))
        if config.user == "": config.user = fernet_decrypt(os.getenv("APT_FTPUSER"))
        if config.passwort == "": config.passwort = fernet_decrypt(os.getenv("APT_FTPPW"))
    else:
        if config.url == "":  config.url = fernet_decrypt(os.getenv("APT_DBURL"))
        if config.user == "": config.user = fernet_decrypt(os.getenv("APT_DBUSER"))
        if config.passwort == "": config.passwort = fernet_decrypt(os.getenv("APT_DBPW"))
        if config.dbname == "": config.dbname = fernet_decrypt(os.getenv("APT_DB"))
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
def LOCAL_read(file_name):
    alt = {}
    if os.path.exists(os.path.join(current_dir, file_name)):
        with open(os.path.join(current_dir, file_name), 'r') as file:
            for line in file:
                item, anzahl = line.split("=")
                alt[item] = anzahl
    return alt
def LOCAL_write(file_name,data:dict):
    with open(os.path.join(current_dir, file_name), 'w') as file:
        for item, anzahl in data.items():
            file.write(f"{item}={anzahl}\n")
def FTP_read(ftpurl,ftpuser,ftppw,file_name):
    alt = {}
    def writealt(line):
        item, anzahl = line.split("=")
        alt[item] = anzahl
    with FTP_TLS(ftpurl,ftpuser,ftppw) as ftp_connection:
        try:
            # ftp_connection.retrlines(f"RETR {file_name}", lambda line: file.write(f"{line}\n"))
            ftp_connection.retrlines(f"RETR {file_name}", writealt)
            return alt
        except Exception as e:
            return None
def FTP_write(ftpurl,ftpuser,ftppw,file_name,data:dict):
    with open(file_name, 'w') as file:
        for item, anzahl in data.items():
            file.write(f"{item}={anzahl}\n")
    success = True
    with open(file_name, 'rb') as file:
        with FTP_TLS(ftpurl,ftpuser,ftppw) as ftp_connection:
            try:
                ftp_connection.storlines(f"STOR {file_name}", file)
            except Exception as e:
                success = False
    if success == True: os.remove(file_name)
def DB_read(mycursor,tracker,name):
    alt = {}
    mycursor.execute('SELECT * FROM APTracking WHERE ID = %s and Game = %s', (tracker, name))
    for line in mycursor.fetchall(): 
        dummy1, dummy2, item, anzahl = line
        alt[item] = anzahl
    return alt
def DB_write_update(mycursor,tracker:str,name:str,alt:dict,neu:dict):
    for item, anzahl in neu.items():
        if (item in alt):
            if int(anzahl) > int(alt[item]):
                mycursor.execute('UPDATE APTracking SET Anzahl = %s WHERE ID = %s AND Game = %s AND Item = %s', (anzahl, tracker, name, item))
        else:
            mycursor.execute('INSERT INTO APTracking (ID, Game, Item, Anzahl) VALUES(%s, %s, %s, %s)', (tracker, name, item, anzahl))
def DB_write_clean(mycursor,tracker:str,name:str,neu:dict):
    values = []
    for item, anzahl in neu.items():
        values.append((tracker, name, item, int(anzahl)))
    mycursor.execute('DELETE FROM APTracking WHERE ID = %s AND Game = %s', (tracker, name))
    mycursor.executemany('INSERT INTO APTracking (ID, Game, Item, Anzahl) VALUES (%s, %s, %s, %s)', values)
def DB_clean_id(mycursor,tracker:str):
    mycursor.execute('DELETE FROM APTracking WHERE ID = %s', [tracker])
def DB_clean_all(mycursor):
    mycursor.execute('DELETE FROM APTracking WHERE 1=1')
def update_gui(fenster):
    modus = varlist["modus"].get()
    for child in fenster.children.values():
        if("name" in child.__dict__): 
            if child.name == "DBNameText" or child.name == 'DBName':
                if modus.startswith("DB"):
                    if child.align == Roemdules.gui.ALIGN_CENTER: child.place(x = (fenster.winfo_width() - child.winfo_reqwidth()) // 2, y = child.element_top)
                    elif child.align == Roemdules.gui.ALIGN_LEFT: child.place(x = 0, y = child.element_top)
                else:
                    child.place_forget()
            elif child.name == "UrlText" or child.name == 'Url' or child.name == "UserText" or child.name == 'User' or child.name == "PasswortText" or child.name == 'Passwort' :
                if modus.startswith("DB") or modus.startswith("FTP"):
                    if child.align == Roemdules.gui.ALIGN_CENTER: child.place(x = (fenster.winfo_width() - child.winfo_reqwidth()) // 2, y = child.element_top)
                    elif child.align == Roemdules.gui.ALIGN_LEFT: child.place(x = 0, y = child.element_top)
                else:
                    child.place_forget()
            
###############################################################################################

try:
    config = Config()
    fenster, varlist = Roemdules.gui.erstelle_Fenster(
        [{"type":"button", "text":"Start", "command":"get_config_from_window(fenster, config)", "width":5, "height":1, "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"radiobutton", "command":"update_gui(fenster)", "variable":"modus", "value":"LOCAL", "text": "Save local", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"radiobutton", "command":"update_gui(fenster)", "variable":"modus", "value":"FTP", "text": "Save via FTP", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"radiobutton", "command":"update_gui(fenster)", "variable":"modus", "value":"DB", "text": "Save via DB", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"radiobutton", "command":"update_gui(fenster)", "variable":"modus", "value":"DB-CLEAN", "text": "Save via DB and empty before", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"radiobutton", "command":"update_gui(fenster)", "variable":"modus", "value":"DB_DEL", "text": "Delete all DB Data with AP ID", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"radiobutton", "command":"update_gui(fenster)", "variable":"modus", "value":"DB_DELALL", "text": "Delete all DB Data", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"Player Name (Part):", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":30, "name":"Name", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"AP Tracker ID", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":30, "name":"Tracker", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"FTP/DB Url:", "name":"UrlText", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":30, "name":"Url", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"FTP/DB UserName:", "name":"UserText", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":30, "name":"User", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"FTP/DB Password:", "name":"PasswortText", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":30, "show":"*", "name":"Passwort", "align":Roemdules.gui.ALIGN_LEFT}
        ,{"type":"label", "text":"DB DBName:", "name":"DBNameText", "align":Roemdules.gui.ALIGN_CENTER}
        ,{"type":"entry", "width":30, "name":"DBName", "align":Roemdules.gui.ALIGN_LEFT}]
        ,fenster_name = "Start", protocols = (("WM_DELETE_WINDOW", "beenden()"),)
        ,context = {'beenden': beenden, 'config': config, 'get_config_from_window': get_config_from_window, 'update_gui': update_gui, 'modus': 'LOCAL'}
        )
    # init_gui(fenster)
    update_gui(fenster)
    fenster.mainloop()
    config.modus = varlist["modus"].get()
    if getattr(sys, 'frozen', False):  # wenn mit PyInstaller "eingefroren"
        # sys.executable ist dann die .exe-Datei 
        current_dir = os.path.dirname(sys.executable)
    else:
        # normale Python-Ausführung: Skriptdatei
        current_dir = os.path.dirname(os.path.abspath(__file__))
    env_datei = os.path.join(current_dir, "env", "APTracking.env")
    if os.path.exists(env_datei):
        get_config_from_file(env_datei, config)
    if config.modus.startswith("DB"):
        mydb = mysql.connector.connect(host=config.url,user=config.user,password=config.passwort,database=config.dbname)
        mycursor = mydb.cursor()
    if config.modus == "DB_DELALL":
        DB_clean_all(mycursor)
        mydb.commit()
    elif config.modus == "DB_DEL":
        DB_clean_id(mycursor,config.tracker)
        mydb.commit()
    else:
        link    = f"https://archipelago.gg/tracker/{config.tracker}"
        seite = urllib.request.urlopen(link)
        soup = BeautifulSoup(seite, "html.parser")
        aptracker = soup.find("table", id="checks-table")
        tds = aptracker.find_all("td")
        name = ""
        for i in range(len(tds)-7):
            if i % 7 == 0:
                link = f'https://archipelago.gg{tds[i].find("a")["href"]}'
            elif i % 7 == 1:
                name = str(tds[i].contents[0])
                file_name = f"{config.tracker}_{name}.txt"
            elif i % 7 == 2 and name.count(config.name) > 0:
                game = str(tds[i].contents[0])
                neu = einzeltracker_drurchgehen(link)
                if config.modus == "LOCAL":
                    alt = LOCAL_read(file_name)
                elif config.modus == "FTP":
                    alt = FTP_read(config.url,config.user,config.passwort,file_name)
                else:
                    alt = DB_read(mycursor,config.tracker,name)
                diff = [f"{name}: {game}", " "]
                for item, anzahl in neu.items():
                    if (item in alt):
                        if int(anzahl) > int(alt[item]):
                            diff.append(f"{item}: {int(anzahl) - int(alt[item])}")
                    else:
                        diff.append(f"{item}: {anzahl}")
                widgets = []
                for difference in diff:
                    widgets.append({"type":"label", "text":difference, "align":Roemdules.gui.ALIGN_LEFT})
                fenster = Roemdules.gui.erstelle_Fenster(widgets,fenster_name = game,fenster_breite=200)
                fenster.mainloop()
                if config.modus == "LOCAL":
                    LOCAL_write(file_name,neu)
                elif config.modus == "FTP":
                    FTP_write(config.url,config.user,config.passwort,file_name,neu)
                elif config.modus == "DB":
                    DB_write_update(mycursor,config.tracker,name,alt,neu)
                    mydb.commit()
                elif config.modus =="DB-CLEAN":
                    DB_write_clean(mycursor,config.tracker,name,neu)
                    mydb.commit()
            else:   
                pass
except Exception as e:
    print(f"{e.__class__}: {e}")