from youtubesearchpython import VideosSearch, Playlist
from tkinter.ttk import OptionMenu, Progressbar
from tkinter.ttk import *
from tkinter import filedialog, Tk, Entry, Button, HORIZONTAL, StringVar
from icecream import ic
import yt_dlp
import threading
import httpx
import os
import json

class masterGui:
    def __init__(self) -> None:
        self.links : list[dict[str]] | None = [] # dict: {"Links":"", "Titel":""}
        self.option : str | None = None
        self.path : str = ""
        self.logger : bool = True
        self.debug : bool = True

        self.frame = Tk()
        self.frame.title("MP4 Downloader")
        self.frame.geometry("370x120")
        self.frame.minsize(370, 120)
        self.frame.configure(background= "#288BA8")

        self.videoLinkEntryField = Entry(self.frame)#Eingabefeld
        self.videoLinkEntryField.place(x= 10, y= 40, width= 310, height= 30)#Zahl der Abgrenzung 148

        self.addbtn = Button(master= self.frame, text= "Add", command= self.add, background= "#FFCE30")
        self.addbtn.place(x= 325, y= 40, width= 35, height= 30)
        
        self.startBtn = Button(master= self.frame, text= "Download", command= self.start, background= "#FFCE30")
        self.startBtn.place(x= 165, y= 80, width= 65, height= 30)#Startknopf für den Download und das laden der Daten

        self.browseDirPathBtn = Button(master= self.frame, text= "Speicherort festlegen", command= self.setDefaultDir, background= "#FFCE30")
        self.browseDirPathBtn.place(x= 235, y= 80,width= 125, height= 30)#Pfadsuchbutton - öffnet Filedialogmenu

        self.setAsDefaultBtn = Button(master= self.frame, text="Standard", command=self.setDefaultFormat, background="#FFCE30")
        self.setAsDefaultBtn.place(x= 90, y= 80, width= 70, height= 30)
        
        self.progressBar = Progressbar(master= self.frame, orient=HORIZONTAL)
        self.progressBar.place(x= 10, y= 10, width= 350, height= 20)
        
    def run(self):
        OPTIONS : list = ['webm', 'mp4', 'mp3', 'wav']
        strVar = StringVar()
        strVar.set(OPTIONS[0])
        self.optionMenu = OptionMenu(self.frame, strVar, *OPTIONS, command= self.select)
        self.optionMenu.place(x= 10, y= 80, width= 75, height= 30)

        self.frame.mainloop()

    def select(self, choice): # Checkt was von der Optionsliste ausgewählt wurde und passt Daten zur Weiterverarbeitung an
        self.option : str = choice

    def start(self):#sammelt Infos und ruft die Add Methode von Client auf
        """Threadstart"""
        self.t1 = threading.Thread(target=self.download)

        if self.t1.is_alive():
            self.t1.join()
            
        else:
            self.t1.start()

    def add(self):
        data : str = self.videoLinkEntryField.get()
        self.links.append({"Links": data, "Titel":""})

    def getDefault(self):
        with open(f"{os.path.dirname(__file__)}\\options.json",'r') as file:
            data = file.read()
            data = json.loads(data)

        return data

    def getDefaultDir(self):
        with open(f"{os.path.dirname(__file__)}\\options.json",'r') as file:
            data = file.read()
            data = json.loads(data)

        return data['defaults']['path']
    
    def setDefaultDir(self):
        text : str = filedialog.askdirectory()
        if text != '':
            data : dict = self.getDefault()
            data['defaults']['path'] = text  
            with open(f"{os.path.dirname(__file__)}\\options.json",'w') as file:
                json.dump(data, file, sort_keys= True, indent= 4)

    def setDefaultFormat(self):
        data = self.getDefault()
        with open(f"{os.path.dirname(__file__)}\\options.json",'w') as file:
            data['defaults']['codec'] = self.option
            json.dump(data, file, sort_keys= True, indent= 4)

    def getInfoDict(self) -> dict:
        """
        Gibt das Infodict zurück, welches benötigt wird um festzulegen in welcher Form
        das Video heruntergeladen werden soll! Als default wird als .webm heruntergeladen
        Default Path: selber Programm ordner
        """
        with open(f"{os.path.dirname(__file__)}\\options.json",'r') as file:
            data = file.read()
            data = json.loads(data)

            self.path = f"{self.path}{'/%(title)s.%(ext)s'}"
            if data.get("options").get(self.option) is not None:
                infoDict : dict = data["options"][self.option]
                infoDict["outtmpl"] = self.path

            else:
                #webm
                infoDict = {
                    'outtmpl': self.path,
                    'noplaylist' : True,
                    'format':'bestvideo+bestaudio/best'
            }
            
            file.close()

        if self.debug:
            ic(f"[getInfoDict]: {infoDict}")
        return infoDict
        
    def request(self):
        """
        Sammelt alles nötige für den Download und gibt das dann zurück
        """
        try:
            for links in self.links:
                if links['Links'].__contains__("&list"):
                    result : dict | str | None = Playlist.getVideos(self.links['links'])
                    self.links.pop(0)

                    for element in result['videos']:
                        for el in element:
                            self.links.append({"Links": el['link'], "Titel": el['title']})    

                    format : dict = self.getInfoDict()
                    if self.logger:
                        format.update((('logger', self.Logger()), ('progress_hooks',[self.myHook]), ('noplaylist', False)))
                    
                    format = yt_dlp.YoutubeDL(format)

                else:
                    links = []
                    for link in self.links:
                        format : dict = self.getInfoDict()
                        if self.logger:
                            format.update((('logger', self.Logger()),('progress_hooks',[self.myHook]), ('noplaylist', True)))
                        
                        if len(self.links) > 1:
                            format["noplaylist"] = False

                        format = yt_dlp.YoutubeDL(format)
                        videosSearch = VideosSearch(link['Links'], limit= 1)
                        result : dict | str = videosSearch.result()           
                        links.append({"Links":result['result'][0]['link'], "Titel":result['result'][0]['title']})
                    
                    self.links.clear()
                    self.links = links

                if self.debug:
                    ic(f"[request]: {format}")  
                return format    

        except httpx.ConnectError:
            return None

    def download(self):
        """
        Nach dem alle nötigen Daten gesammelt wurden, wird der Download veranlasst
        """
        ydl = self.request()
        if self.links != []:
            for element in self.links:
                with ydl:
                    try:
                        if self.debug:
                            ic(f"Downloading: {self.links}")

                        ydl.extract_info(element['Links'])

                    except yt_dlp.utils.DownloadError:
                        return f"Video nicht verfügbar {element}"
            self.links.clear()

        else:
            print("Keine Daten vorhanden")

    # Logs

    class Logger(object):
            def __init__(self) -> None:
                pass
            """
            Stellt fest ob es Probleme mit den angefragen Inhalten gibt

            //Todo Verfahren bei nicht verfügbaren Inhalten
            """
            def debug(self, msg):
                return (f"From Logger Objekt - Debug: {msg}")

            def warning(self, msg):
                return (f"From Logger Objekt - Warning: {msg}")

            def error(self, msg):
                return msg
            
    def __str__(self):
        ic(self.links, self.option, self.path)
        return "Konverter"

    def myHook(self, d : dict):
        """
        Trackt den Downlaod Status
        """
        filename : str= d['filename']#muss noch geprüft werden (debuggen) - was macht das hier
        filename = filename.split(".")[0] 
        
        if d['status'] == "downloading":
            ic(d.get('total_bytes') != None)
            if d.get('total_bytes') != None:
                totalBytes : int = d['total_bytes']
                downloadedBytes = d['downloaded_bytes']
                return f"Video zu: {(downloadedBytes / totalBytes)*100}% heruntergeladen"
                    
            else: 
                ic(d.get('_percent_str') != None)
                if d.get('_percent_str') != None:
                    ic(float(d.get('_percent_str').split("%")[0]))
                    self.progressBar.configure(value=float(d.get('_percent_str').split("%")[0]))
                return None
            
        if d['status'] == "finished":
            return "Alle eingefügten Links werden automatisch gedownloaded, nach dem drücken des Download Buttons"

if __name__ == "__main__":
    myKonverter = masterGui()
    myKonverter.run()
