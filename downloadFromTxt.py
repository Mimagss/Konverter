from old import Mimags_Konverter
import filter
import os

DIR_PATH: str = os.path.dirname(__file__)
songs: list = filter.read_file(file_path=f"{DIR_PATH}/martinLiederOhneDuplikate.txt")
konv = Mimags_Konverter.Konverter()

# download routine neu schreiben, kommt nicht mit mehreren argumenten klar
print("Downloading")
konv.download(logger=False, option="mp3", path=f"{DIR_PATH}/musicMartin", givenLinks=songs)
print("finished")











