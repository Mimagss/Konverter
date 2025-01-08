import os
from icecream import ic
ic.configureOutput(prefix="Debug: ", includeContext=True)

def write_youtube_links(file_path: str) -> None:
    """
    Schreibt eine Liste von YouTube-Links in eine .txt-Datei, 
    wobei jeder Link in eine neue Zeile geschrieben wird.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for link in new_links:
                file.write(link + '\n')
            ic("fertig")
            
    except Exception as e:
        ic(f"Fehler beim Schreiben in die Datei {file_path}: {e}")
        
    finally:
        file.close()
        ic("file geschlossen")

def read_youtube_links(file_path: str) -> list[str]:
    """Liest eine Datei ein und gibt eine Liste von YouTube-Links zurück."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Alle Zeilen lesen und führende/trailing Whitespaces entfernen
            links = [line.strip() for line in file if line.strip()]
            
        return links
    except FileNotFoundError:
        print(f"Datei {file_path} nicht gefunden.")
        return []

def filter_duplicates(arg: list) -> list:
    """Entfernt Duplikate aus einer Liste, während die ursprüngliche Reihenfolge der Elemente beibehalten wird."""
    result: list = []

    for index, element in enumerate(arg):
        # bei bereits vorhanden elementen in der liste
        if element in result:
            continue
        result.append(element)
    return result


# Beispiel für die Nutzung
if __name__ == "__main__":
    filename: str = "martinLieder"
    file_path: str = f"{os.path.dirname(__file__)}/{filename}.txt"
    youtube_links: list = read_youtube_links(file_path)
    new_links = filter_duplicates(youtube_links)
    
    for index, element in enumerate(new_links):
        ic(index, element)
        
    write_youtube_links(file_path=f"{os.path.dirname(__file__)}/{filename}OhneDuplikate.txt")