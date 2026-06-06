import speech_recognition as sr
import pyttsx3
import os
import google.generativeai as genai
import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import webbrowser
import pyautogui
import time
import requests # install library: pip install LIBRARY

# 1. KONFIGURACJA AI
genai.configure(api_key="HERE PASTE API KEY")
model = genai.GenerativeModel('models/gemini-3.1-flash-lite-preview')


# 2. ZARZĄDZANIE PLIKAMI
PLIK_PAMIECI = "moje_komendy.json"
PLIK_USTAWIEN = "ustawienia.json"

def wczytaj_json(nazwa_pliku, domyslne):
    if os.path.exists(nazwa_pliku):
        with open(nazwa_pliku, "r", encoding="utf-8") as plik:
            return json.load(plik)
    return domyslne

def zapisz_json(nazwa_pliku, dane):
    with open(nazwa_pliku, "w", encoding="utf-8") as plik:
        json.dump(dane, plik, indent=4)

baza_komend = wczytaj_json(PLIK_PAMIECI, {})
ustawienia = wczytaj_json(PLIK_USTAWIEN, {"jezyk": "speech_recognition", "szybkie_szukanie": True, "ai_limit": 500})

ai_aktywne = False
licznik_ai = 0

# 3. FUNKCJE GŁOSOWE
def mow(tekst):
    print(f"Felix: {tekst}")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if ustawienia["jezyk"] == "pl-PL" and "Polish" in voice.name:
            engine.setProperty('voice', voice.id)
        elif ustawienia["jezyk"] == "en-US" and "English" in voice.name:
            engine.setProperty('voice', voice.id)
    
    engine.say(tekst)
    engine.runAndWait()
    engine.stop()

def sluchaj_w_tle():
    r = sr.Recognizer()
    with sr.Microphone() as zrodlo:
        r.adjust_for_ambient_noise(zrodlo, duration=0.5)
        print(f"... Nasłuchuję ({ustawienia['jezyk']}) ...")
        try:
            audio = r.listen(zrodlo, phrase_time_limit=5)
            tekst = r.recognize_google(audio, language=ustawienia["jezyk"]).lower()
            print(f"[DEBUG] Usłyszałem: '{tekst}'")
            return tekst
        except:
            return ""

# 4. FUNKCJA STEROWANIA SERWEM
def steruj_swiatlem(akcja):
    ip_esp = "HERE PASTE ESP IP" 
    
    try:
        if akcja == "on":
            requests.get(f"http://{ip_esp}/OFF", timeout=2)
        else:
            requests.get(f"http://{ip_esp}/ON", timeout=2)
    except:
        mow("")

# 5. FUNKCJE GUI I USTAWIENIA
def pobierz_tekst_z_okienka(tytul, tresc):
    root = tk.Tk()
    root.withdraw()
    wpisany_tekst = simpledialog.askstring(tytul, tresc)
    root.destroy()
    return wpisany_tekst

def otworz_ustawienia():
    root = tk.Tk()
    root.title("Felix Settings")
    root.geometry("300x250")

    def zapisz_i_zamknij():
        ustawienia["jezyk"] = "pl-PL" if var_lang.get() == 1 else "en-US"
        ustawienia["szybkie_szukanie"] = True if var_search.get() == 1 else False
        zapisz_json(PLIK_USTAWIEN, ustawienia)
        root.destroy()
        if ustawienia["jezyk"] == "pl-PL":
            mow("Ustawienia zostały zaktualizowane.")
        else:
            mow("Settings have been updated.")

    var_lang = tk.IntVar(value=1 if ustawienia["jezyk"] == "pl-PL" else 2)
    var_search = tk.IntVar(value=1 if ustawienia["szybkie_szukanie"] else 0)

    tk.Label(root, text="Język systemu (Language):", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Radiobutton(root, text="Polski", variable=var_lang, value=1).pack()
    tk.Radiobutton(root, text="English", variable=var_lang, value=2).pack()

    tk.Label(root, text="Tryb wyszukiwania (Search Mode):", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Checkbutton(root, text="Błyskawiczne / Instant (bez pisania)", variable=var_search).pack()

    tk.Button(root, text="ZAPISZ / SAVE", command=zapisz_i_zamknij, bg="green", fg="white").pack(pady=20)
    root.mainloop()

# --- NOWOŚĆ: MENU POMOCY ---
def pokaz_pomoc():
    root = tk.Tk()
    root.title("Felix - Pomoc / Help")
    root.geometry("450x500")

    tk.Label(root, text="Dostępne Komendy / Available Commands", font=("Arial", 12, "bold")).pack(pady=10)

    # Ramka z suwakiem dla długiej listy
    ramka = tk.Frame(root)
    ramka.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    suwak = tk.Scrollbar(ramka)
    suwak.pack(side=tk.RIGHT, fill=tk.Y)
    
    pole_tekstowe = tk.Text(ramka, wrap=tk.WORD, yscrollcommand=suwak.set, bg="#f9f9f9", font=("Arial", 10))
    pole_tekstowe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    suwak.config(command=pole_tekstowe.yview)

    # Przygotowanie treści pomocy
    tresc = "--- SYSTEMOWE / SYSTEM ---\n"
    tresc += "• wyszukaj / search [hasło] - Wyszukiwanie w Google / search in Google\n"
    tresc += "• [adres].com / .pl - Wchodzi prosto na stronę WWW / Goes straight to the website\n"
    tresc += "• ustawienia / settings - Panel języka i wyszukiwania / Language and Search Panel\n"
    tresc += "• włącz/wyłącz AI / enable/disable AI - Przełącznik sztucznej inteligencji / AI Switch\n"
    tresc += "• wpisz / type - Okienko do wpisania komendy klawiaturą / Text box for entering a command using the keyboard\n"
    tresc += "• stwórz nowe polecenie / dodaj komendę / add command - Kreator własnych programów / Custom Program Creator\n"
    tresc += "• usuń komendę / remove command - Usuwa zapisany program / Deletes the saved program\n"
    tresc += "• status - Informacje o stanie Felixa / Information about Felix's condition\n"
    tresc += "• pomoc / help - Wyświetla to okno / This displays the window\n"
    tresc += "• koniec / exit / turn off - Wyłączenie asystenta / Turn off the assistant\n\n"

    tresc += "--- TWOJE WŁASNE / YOUR COMMANDS ---\n"
    if not baza_komend:
        tresc += "(Brak zapisanych komend / No custom commands saved)\n"
    for nazwa, sciezka in baza_komend.items():
        tresc += f"• {nazwa} -> {sciezka}\n"

    # Wstawiamy treść i blokujemy możliwość edycji przez użytkownika
    pole_tekstowe.insert(tk.END, tresc)
    pole_tekstowe.config(state=tk.DISABLED)

    tk.Button(root, text="ZAMKNIJ / CLOSE", command=root.destroy, bg="#d9534f", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
    root.mainloop()

# 6. EFEKTOWNE WYSZUKIWANIE
def szukaj_w_internecie(haslo):
    if ustawienia["szybkie_szukanie"]:
        mow(f"Otwieram wyniki dla: {haslo}" if ustawienia["jezyk"] == "pl-PL" else f"Opening results for: {haslo}")
        url = f"https://www.google.com/search?q={haslo}"
        webbrowser.open(url)
    else:
        mow(f"Szukam: {haslo}" if ustawienia["jezyk"] == "pl-PL" else f"Searching for: {haslo}")
        webbrowser.open("https://www.google.com")
        time.sleep(2.5)
        pyautogui.write(haslo, interval=0.1)
        pyautogui.press('enter')

# 7. MÓZG OPERACYJNY
def wykonaj_komende(zapytanie):
    global ai_aktywne, licznik_ai
    
    # --- NOWOŚĆ: POMOC ---
    if "pomoc" in zapytanie or "help" in zapytanie:
        mow("Otwieram panel pomocy." if ustawienia["jezyk"] == "pl-PL" else "Opening help panel.")
        pokaz_pomoc()
        return "ok"

    # ŚWIATŁO
    if "włącz światło" in zapytanie or "zapal światło" in zapytanie or "turn on lights" in zapytanie:
        mow("zapalam światło." if ustawienia["jezyk"] == "pl-PL" else "i am turning the lights on.")
        steruj_swiatlem("on")
        return "ok"
    
    if "wyłącz światło" in zapytanie or "zgaś światło" in zapytanie or "turn off lights" in zapytanie:
        mow("zgaszam światło." if ustawienia["jezyk"] == "pl-PL" else "i am turning the lights off.")
        steruj_swiatlem("off")
        return "ok"

    # USTAWIENIA
    if "settings" in zapytanie or "ustawienia" in zapytanie:
        mow("Otwieram panel ustawień." if ustawienia["jezyk"] == "pl-PL" else "Opening settings.")
        otworz_ustawienia()
        return "ok"

    # ADRESY WWW
    domeny = (".com", ".pl", ".net", ".org", ".tv")
    if zapytanie.strip().endswith(domeny):
        adres = zapytanie.strip().replace(" ", "")
        mow(f"Wchodzę na {adres}" if ustawienia["jezyk"] == "pl-PL" else f"Going to {adres}")
        webbrowser.open(f"https://{adres}")
        return "ok"

    # WYSZUKAJ
    if "wyszukaj" in zapytanie or "znajdź" in zapytanie or "search" in zapytanie:
        haslo = zapytanie.replace("wyszukaj", "").replace("znajdź", "").replace("search", "").strip()
        if haslo: szukaj_w_internecie(haslo)
        return "ok"

    # WŁĄCZ/WYŁĄCZ AI
    if "wyłącz ai" in zapytanie or "disable ai" in zapytanie:
        ai_aktywne = False
        mow("AI wyłączone." if ustawienia["jezyk"] == "pl-PL" else "AI disabled.")
        return "ok"
    elif "włącz ai" in zapytanie or "enable ai" in zapytanie:
        ai_aktywne = True
        mow("AI włączone." if ustawienia["jezyk"] == "pl-PL" else "AI enabled.")
        return "ok"
        
    # STATUS I KONIEC
    elif "status" in zapytanie:
        mow(f"System OK. AI: {ai_aktywne}")
        return "ok"
    elif "koniec" in zapytanie or "exit" in zapytanie:
        mow("Dobranoc." if ustawienia["jezyk"] == "pl-PL" else "Goodbye.")
        return "koniec"
        
# ZARZĄDZANIE KOMENDAMI
    elif "stwórz nowe polecenie" in zapytanie or "dodaj komendę" in zapytanie or "add command" in zapytanie or "create command" in zapytanie:
        mow("Otwieram kreator." if ustawienia["jezyk"] == "pl-PL" else "Opening creator.")
        
        # Wybór tekstów do okienek w zależności od języka
        tytul = "Kreator Komend" if ustawienia["jezyk"] == "pl-PL" else "Command Creator"
        tresc_nazwa = "Nazwa komendy:" if ustawienia["jezyk"] == "pl-PL" else "Command name:"
        tresc_sciezka = "Ścieżka do pliku:" if ustawienia["jezyk"] == "pl-PL" else "File path:"
        
        nazwa = pobierz_tekst_z_okienka(tytul, tresc_nazwa)
        sciezka = pobierz_tekst_z_okienka(tytul, tresc_sciezka)
        
        if nazwa and sciezka:
            baza_komend[nazwa.lower().strip()] = sciezka.strip()
            zapisz_json(PLIK_PAMIECI, baza_komend)
            mow("Gotowe." if ustawienia["jezyk"] == "pl-PL" else "Done.")
        return "ok"
    
    elif "usuń komendę" in zapytanie or "delete command" in zapytanie or "remove command" in zapytanie:
        mow("Co mam usunąć?" if ustawienia["jezyk"] == "pl-PL" else "What should I delete?")
        
        # Wybór tekstów do okienek
        tytul = "Usuwanie" if ustawienia["jezyk"] == "pl-PL" else "Deleting"
        tresc = "Wpisz nazwę:" if ustawienia["jezyk"] == "pl-PL" else "Enter name:"
        
        nazwa = pobierz_tekst_z_okienka(tytul, tresc)
        
        if nazwa and nazwa.lower() in baza_komend:
            del baza_komend[nazwa.lower()]
            zapisz_json(PLIK_PAMIECI, baza_komend)
            mow("Usunięto." if ustawienia["jezyk"] == "pl-PL" else "Deleted.")
        else:
            if nazwa: # Powie to tylko, jeśli wpiszesz nazwę, a nie gdy po prostu zamkniesz okienko
                mow("Nie znalazłem takiej komendy." if ustawienia["jezyk"] == "pl-PL" else "Command not found.")
        return "ok"
    
    # WŁASNE KOMENDY Z PLIKU
    for nazwa, sciezka in baza_komend.items():
        if nazwa in zapytanie:
            mow(f"Odpalam {nazwa}" if ustawienia["jezyk"] == "pl-PL" else f"Opening {nazwa}")
            try: os.startfile(sciezka)
            except: mow("Błąd ścieżki." if ustawienia["jezyk"] == "pl-PL" else "Path error.")
            return "ok"

    # AI
    if zapytanie != "" and ai_aktywne:
        if licznik_ai < ustawienia["ai_limit"]:
            licznik_ai += 1
            print("Felix myśli...")
            odp = model.generate_content(f"Jesteś asystentem o imieniu Felix. Odpowiadaj krótko w języku: {ustawienia['jezyk']}. Pytanie: {zapytanie}")
            mow(odp.text)
        else:
            mow("Limit AI wykorzystany." if ustawienia["jezyk"] == "pl-PL" else "AI limit reached.")
    
    return "ok"

# --- START ---
mow("Felix gotowy." if ustawienia["jezyk"] == "pl-PL" else "Felix is ready.")

while True:
    komenda = sluchaj_w_tle()
    
    if "felix" in komenda or "feliks" in komenda or "phoenix" in komenda:
        zapytanie = komenda.replace("felix", "").replace("feliks", "").replace("phoenix", "").strip()
        
        if zapytanie:
            if "wpisz" in zapytanie or "wpisać" in zapytanie or "type" in zapytanie or "enter" in zapytanie:
                if ustawienia["jezyk"] == "pl-PL":
                    mow("Otwieram panel tekstowy.")
                    tekst = pobierz_tekst_z_okienka("System Felix", "Wpisz polecenie:")
                else:
                    mow("Opening text panel.")
                    tekst = pobierz_tekst_z_okienka("System Felix", "Type your command:")
                
                if tekst:
                    if wykonaj_komende(tekst.lower()) == "koniec": break
            
            else:
                if wykonaj_komende(zapytanie) == "koniec": break