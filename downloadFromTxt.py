from youtubesearchpython import VideosSearch
from youtubesearchpython import *
import yt_dlp
from icecream import ic
ic.configureOutput(prefix= "Debug: ", includeContext=True)
import filter
import os

DIR_PATH: str = os.path.dirname(__file__)
path: str = f"{DIR_PATH}/martinLiederOhneDuplikate.txt"
songs: list = filter.read_file(file_path=path)
infoDict = {
    'outtmpl': path + '/%(title)s.%(ext)s',
    'format': 'bestaudio/best',
    'noplaylist' : True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3'
    }]
}

linksToDownload: list = [{
    "link":"",
    "title":""
}]

def request(link):
    format = yt_dlp.YoutubeDL(infoDict)
    videosSearch = VideosSearch(link, limit= 1)
    result : dict | str = videosSearch.result()           

    linksToDownload.append({
        "link":result['result'][0]['link'],
        "title":result['result'][0]['title']
    })
    
    return format

def download(givenLinks: str):
    # muss noch gedebugged werden
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

        ydl = request(givenLinks)
        if linksToDownload != []:
            for element in linksToDownload:
                with ydl:
                    try:
                        ydl.extract_info(element.get("link"))
                    
                    except yt_dlp.utils.DownloadError:
                        return f"Video nicht verfügbar {element}"

# download routine neu schreiben, kommt nicht mit mehreren argumenten klar
print("Downloading")
for song in songs:
    download(song)
print("finished")











