from youtubesearchpython import VideosSearch
from youtubesearchpython import *
from icecream import ic
import yt_dlp
import httpx
import os
import json

"""
Dict neu Struckturiren:
self.links = [
    {
        "Links": "", "Titel": ""
    },
]
zugriff:
links = self.links[i]["Links"]
Titel = self.links[i]["Titel"]
"""
class Konverter:
    def __init__(
            self, 
            links : list[dict[str]] = [{"Links":"", "Titel":""}], 
            option : str | None = None, 
            path : str  = "/music", 
            debug : bool = False, 
            logger : bool = False) -> None:
        
        self.links = links # Alle angeforderten Links
        self.option = option # Angeforderte option für die Links
        self.path = path
        self.debug = debug
        self.logger = logger

    def __str__(self):
        return "ich bin der Konverter"

    def getInfoDict(self) -> dict:
        """
        Gibt das Infodict zurück, welches benötigt wird um festzulegen in welcher Form
        das Video heruntergeladen werden soll! Als default wird als .webm heruntergeladen
        Default Path: selber Programm ordner
        """
        with open(f"{os.path.dirname(__file__)}\\options.json",'r') as file:
            data = file.read()
            data = json.loads(data)

            if data.get("options").get(self.option) is not None:
                infoDict : dict = data["options"][self.option]
                infoDict["outtmpl"] = f"{self.path}/{'%(title)s.%(ext)s'}"
            else:
                #webm
                infoDict = {
                    'outtmpl': f"{self.path}/{'%(title)s.%(ext)s'}",
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

        #TODO: Renaming of local Variables
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
            if d.get('total_bytes') != None:
                totalBytes : int = d['total_bytes']
                downloadedBytes = d['downloaded_bytes']
                return f"Video zu: {(downloadedBytes / totalBytes)*100}% heruntergeladen"
                
            else: 
                if d.get('_percent_str') != None:
                    return float(d.get('_percent_str').split("%")[0])
                return None
            
        if d['status'] == "finished":
            return "Alle eingefügten Links werden automatisch gedownloaded, nach dem drücken des Download Buttons"


if __name__ == "__main__":
    titel = [
    {
        "Links": "Hells Bells", "Titel": "Hells Bells"
    },
    {
        "Links": "Thunderstruck", "Titel": "Thunderstruck"
    },
    {
        "Links": "Metal Maschine", "Titel": "Metal Maschine"
    }]
       
    myKonv = Konverter(
        links = titel,
        option= "mp3",
        path= f"{os.path.dirname(__file__)}/music",
        debug= True,
        logger= True)
    print(myKonv)
    myKonv.download()
