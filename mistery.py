from Crypto.Cipher import AES
import tkinter as tk
from tkinter import messagebox
import sys
import os
import zipfile
import io
import subprocess
import math
import requests
import json
import hashlib
from datetime import datetime

# URL del file JSON con i dati di gioco
url_file_json = 'http://zipo.altervista.org/MindQuest/gamedata.json'

input_folder = None
key = b'123'
versione = "1.0.1"

if key == b'123':
    key = "123"
    key = bytes( key[1:3] + key[2] + 'Billy' + str(format(math.pi, '.7f')).replace('.','') , 'utf-8')

out_file_path = './MisteryData'
    
def encrypt_decrypt_file(input_file, output_file, key, mode='decrypt'):
    chunk_size = 64 * 1024
    if key is not None:
        cipher = AES.new(key, AES.MODE_ECB)

    with open(input_file, 'rb') as in_file:
        with open(output_file, 'wb') as out_file:
            while True:
                chunk = in_file.read(chunk_size)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0 and key is not None:
                    chunk += b' ' * (16 - len(chunk) % 16)  # Padding

                
                if key is None:
                    encrypted_chunk = chunk
                else:
                    if mode == 'encrypt':
                        encrypted_chunk = cipher.encrypt(chunk)
                    else:
                        encrypted_chunk = cipher.decrypt(chunk)

                out_file.write(encrypted_chunk)

def encrypt_folder(input_folder, output_zip, key):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.join(root, file)
                encrypted_file = file_path + '.enc'

                encrypt_decrypt_file(file_path, encrypted_file, key, 'encrypt')
                zipf.write(encrypted_file, os.path.relpath(encrypted_file, input_folder))
                os.remove(encrypted_file)

def decrypt_zip_file(file_to_decrypt, output_file=None, zip_file=out_file_path, key=key):
    file_to_decrypt=str(file_to_decrypt)
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        with zip_ref.open(file_to_decrypt) as encrypted_file:
            encrypted_data = encrypted_file.read()
    
    if key is not None:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_data = cipher.decrypt(encrypted_data)
    else:
        #zip non crittata
        decrypted_data = encrypted_data
    
    if output_file is None:
        return decrypted_data
    else:
        with open(output_file, 'wb') as out_file:
            out_file.write(decrypted_data)
    
    return True
    # Puoi lavorare con i dati decrittati qui, ad esempio stamparli
    print(decrypted_data.decode('utf-8'))  # Decodifica i dati in una stringa


def play_decrypted_video_from_zip(file_to_decrypt, zip_file=out_file_path, key=key):
    if not os.path.isfile(zip_file):
        tk.Tk().iconify()
        messagebox.showwarning("File Mancante", f"Vedrai questo messaggio perchè qui non c'è il file {zip_file}")
        sys.exit();
        
    if not os.path.isfile('./ffplay.exe'):
        decrypt_zip_file('ffplay.exe.enc', 'ffplay.exe')
        
    file_to_decrypt = str(file_to_decrypt)
    decrypted_data = decrypt_zip_file(file_to_decrypt + '.enc')

    cmdline = ['./ffplay', '-x', '480', '-y', '720', '-']
    try:
        ffmpeg_process = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        # Invio dei dati video a ffmpeg
        ffmpeg_process.stdin.write(decrypted_data)
        ffmpeg_process.stdin.close()
        # Attendere che ffmpeg completi l'elaborazione e termini
        ffmpeg_process.wait()
    except:
        tk.Tk().iconify()
        messagebox.showwarning("ok.", "Hai chuso il video?")
        return False
        
    tk.Tk().iconify()
    messagebox.showinfo("Alert", "Clip conclunsa")
    
    return True

def calcola_checksum(file_path):
    #se il file non esiste ritorna none
    if (not os.path.isfile(file_path)):
        return None
     
    # Calcola il checksum del file
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def check_trivia_online(percorso_file_locale=out_file_path):

    # Scarica il file JSON
    response = requests.get(url_file_json)
    if response.status_code == 200:
        json_data = response.json()
        
        # Ottieni il checksum dal file JSON
        checksum_da_json = json_data.get('checksum')

        # Calcola il checksum del file locale
        checksum_locale = calcola_checksum(percorso_file_locale)
        
        nuova_versione = json_data.get('version')
        if nuova_versione is not None and str(nuova_versione) != versione:
            tk.Tk().iconify()
            ok_download = messagebox.askokcancel("Aggiornamento", "Il gioco è da aggiornare, iniziare il download?")
            if not ok_download:
               messagebox.showinfo("I'm too old!", "Il gioco ha bisogno di restare al passo con i tempi.")
               sys.exit()
            url_download_bin = json_data.get('url_download_bin')  # URL del nuovo file eseguibile scaricare
            if url_download_bin:
                # Scarica il nuovo file bin
                response = requests.get(url_download_bin)
                if response.status_code == 200:
                    zip_path = './MindQuest'+nuova_versione
                    with open(zip_path, 'wb') as file:
                        file.write(response.content)
                    
                    #estraggo il file eseguibile
                    decrypt_zip_file('game.exe', zip_path + '.exe', zip_path, None)
                    #rimuovo la zip
                    if os.path.isfile(zip_path):
                        os.remove(zip_path)
                    
        # Se i checksum sono diversi, scarica e sostituisci il file
        if (not os.path.isfile(percorso_file_locale)) or (checksum_da_json and checksum_da_json != checksum_locale):
            
            tk.Tk().iconify()
            ok_download = messagebox.askokcancel("Aggiornamento", "Le CLIP richiedono un aggiornamento, iniziare il download?")
            if not ok_download:
                messagebox.showinfo("I'm too old!", "Bisogna restare al passo con i tempi.")
                sys.exit()
            
            url_download_file = json_data.get('url_download_data')  # URL del nuovo file dati scaricare
            if url_download_file:
                # Scarica il nuovo file data
                response = requests.get(url_download_file)
                if response.status_code == 200:
                    # Scrivi il nuovo file scaricato
                    with open(percorso_file_locale, 'wb') as file:
                        file.write(response.content)

                    tk.Tk().iconify()
                    messagebox.showinfo("File aggiornati con successo!", 
                        """Sono stati aggiunti nuovi contenuti,
                        è richiesto il riavvio del gioco""")
                    # introduce un ritardo di 2 secondi prima di eseguire il nuovo bin e cancellare il corrente
                    if not "python.exe" in sys.executable:
                        os.system(f"start cmd /K \"timeout /t 2 && del /q /s {sys.executable} && {zip_path}.exe\"")
                    sys.exit()

                    
                else:
                    tk.Tk().iconify()
                    messagebox.showinfo("Errore", "Errore durante il download del file di dati.")
            else:
                tk.Tk().iconify()
                messagebox.showinfo("Errore", "URL di download del file non disponibile.")
        else:
            #print("Il file locale è aggiornato, nessuna azione necessaria.")
            return json_data.get('trivia_quest')
    else:
        #print("Impossibile recuperare il file JSON.")
        tk.Tk().iconify()
        messagebox.showinfo("Errore", "Le informazioni chiave online non sono disponibili. Riprova più tardi")
    return None

def get_sequenza_numeri(max_number=5):
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday  # Giorno dell'anno (da 1 a 365/366)
    print(day_of_year)
    # Calcolo della sequenza di numeri univoci da 1 a 40 in base al giorno dell'anno
    start_number = ((day_of_year - 1) % max_number) + 1
    
    if start_number + max_number > max_number:
        return list(range(start_number, max_number+1)) + list(range(1, 5-(max_number-start_number))) 
    else: 
        return list(range(start_number, start_number + 5))


#### Critta cartella
input_folder = './out'
if os.path.isdir(input_folder):
    output_zip = 'MisteryData'
    encrypt_folder(input_folder, output_zip, key)
    os.rename(input_folder, input_folder+'_')
    sys.exit()

    
###Decritta and play:
#file_to_decrypt = '1'

#decritta ffplay
#play_decrypted_video_from_zip(file_to_decrypt)

