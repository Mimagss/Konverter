from youtubesearchpython import VideosSearch
from youtubesearchpython import *
import yt_dlp
import httpx
import os
from icecream import ic
ic.configureOutput(prefix="Debug: ", includeContext=True)

class Konverter:
    def __init__(self) -> None:
        self.links = [] # Alle angeforderten Links
        self.titles = [] # Alle Titel zu den Links

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

    def myHook(self, d : dict):
        """
        Trackt den Downlaod Status
        """
        return
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

    def getInfoDict(self, option : str, path : str) -> dict:
        """
        Gibt das Infodict zurück, welches benötigt wird um festzulegen in welcher Form
        das Video heruntergeladen werden soll!
        """
        if option == 'webm':
            infoDict : dict = {
                'outtmpl': path + '/%(title)s.%(ext)s',
                    'noplaylist' : True,
                    'format':'bestvideo+bestaudio/best'
            }

        elif option == 'mp4':
            infoDict : dict = {
                    'outtmpl': path + '/%(title)s.%(ext)s',
                    'noplaylist' : True,
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio'
                }
            
        elif option == 'mp3':
            infoDict = {
                    'outtmpl': path + '/%(title)s.%(ext)s',
                    'format': 'bestaudio/best',
                    'noplaylist' : True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3'
                    }]
            }

        elif option == 'wav':
            infoDict = {
                    'outtmpl': path + '/%(title)s.%(ext)s',
                    'format': 'bestaudio/best',
                    'noplaylist' : True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav'
                    }]
            }
        
        else: 
            return None
        
        return infoDict

    def getIndexFromList(self, list: list, arg) -> int:
        for index, element in enumerate(list):
            if element == arg:
                return index

    def request(self, givenLinks : list, option : str, path : str = os.path.join(os.path.dirname(os.path.realpath(__file__))), logger : bool = False):
        """
        Sammelt alles nötige für den Download und gibt das dann zurück
        """
        try:
            if givenLinks[0].__contains__("&list"):
                result : dict | str | None = Playlist.getVideos(givenLinks[0])

                for element in result['videos']:
                    for el in element:

                        self.links.append(el['link'])
                        self.titles.append(el['title'])    

                format : dict = self.getInfoDict(option, path)
                if logger:
                    format.update((('logger', self.Logger()), ('progress_hooks',[self.myHook]), ('noplaylist', False)))
                format = yt_dlp.YoutubeDL(format)

            else:
                for element in givenLinks:
                    format : dict = self.getInfoDict(option, path)
                    if logger:
                        format.update((('logger', self.Logger()),('progress_hooks',[self.myHook]), ('noplaylist', True)))
                    format = yt_dlp.YoutubeDL(format)

                    videosSearch = VideosSearch(element, limit= 1)
                    result : dict | str = videosSearch.result()           
                    if result['result'] == []:
                        ic(element)
                        ic(self.getIndexFromList(givenLinks, element))
                        
                    
                    else:     
                        self.links.append(result['result'][0]['link'])
                        self.titles.append(result['result'][0]['title'])
                    
                givenLinks.clear()

            return format    

        except httpx.ConnectError:
            return None

    def download(self, givenLinks : list | str, option : str, path : str = os.path.join(os.path.dirname(os.path.realpath(__file__))), logger = True):
        """
        Nach dem alle nötigen Daten gesammelt wurden, wird der Download veranlasst
        """
        def strToList(str : str):
            """Gibt den Angeforderten Titel als Liste zurück"""
            newList = []
            newList.append(str)
            return newList
        
        if type(givenLinks) == str:
            givenLinks = strToList(givenLinks)

        ydl = self.request(givenLinks, option, path, logger)
        if self.links != []:
            for element in self.links:
                with ydl:
                    try:
                        ydl.extract_info(element)
                        self.links.pop(0)
                        filename = self.titles[0] 
                        self.titles.pop(0)
                        return filename
                    
                    except yt_dlp.utils.DownloadError:
                        return f"Video nicht verfügbar {element}"
        
if __name__ == "__main__":
    konv = Konverter()
    links = []
    links.append(str(input("Links bitte:")))
    konv.download(
        givenLinks=links,
        option="mp3",
        path= "C:/Users/Einbr/Downloads/niceMuke"
    )
