#!/usr/bin/env python3
"""
🤖 JARVIS - Always-on Voice Assistant
Say "Hey Jarvis" to wake up, then give your command.
"""

import speech_recognition as sr
import pyttsx3
import datetime
import threading
import time
import json
import os
import sys
import re
import webbrowser
import subprocess
import random
import platform

# ── CONFIG ───────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"
NEWS_API_KEY        = "YOUR_NEWS_API_KEY_HERE"  # https://newsapi.org (free)
DEFAULT_CITY        = "Chennai"
WAKE_WORDS          = ["hey jarvis", "jarvis"]
REMINDERS_FILE      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reminders.json")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── TTS ───────────────────────────────────────────────────────────────────────
_tts_lock = threading.Lock()

def speak(text: str):
    print(f"  🤖 {text}")
    with _tts_lock:
        try:
            # Use Windows SAPI directly — most reliable on Windows
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = 0
            speaker.Volume = 100
            speaker.Speak(text)
        except Exception:
            # Fallback to pyttsx3
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty("rate", 165)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"  TTS error: {e}")

# ── RECOGNIZER ────────────────────────────────────────────────────────────────
def build_recognizer():
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.7
    return r

def listen_once(recognizer, mic, timeout=3, phrase_limit=8):
    try:
        with mic as source:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        return recognizer.recognize_google(audio).lower()
    except Exception:
        return None

# ── TIME & DATE ───────────────────────────────────────────────────────────────
def handle_time():
    now = datetime.datetime.now()
    speak(f"The current time is {now.strftime('%I:%M %p')}.")

def handle_date():
    now = datetime.datetime.now()
    speak(f"Today is {now.strftime('%A, %B %d, %Y')}.")

# ── WEATHER ───────────────────────────────────────────────────────────────────
def handle_weather(command):
    if not HAS_REQUESTS:
        speak("Requests library not installed."); return
    if OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        speak("No OpenWeather API key set."); return
    match = re.search(r"weather (?:in|at|for) ([a-z\s]+)", command)
    city = match.group(1).strip() if match else DEFAULT_CITY
    try:
        resp = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric", timeout=6)
        if resp.status_code == 200:
            d = resp.json()
            speak(f"Weather in {city.title()}: {d['weather'][0]['description']}, "
                  f"{d['main']['temp']:.0f} degrees, feels like {d['main']['feels_like']:.0f}.")
        else:
            speak(f"Couldn't get weather for {city}.")
    except Exception as e:
        speak(f"Weather error: {e}")

# ── OPEN WEBSITES / APPS ──────────────────────────────────────────────────────
WEBSITES = {
    "youtube":   "https://www.youtube.com",
    "google":    "https://www.google.com",
    "gmail":     "https://mail.google.com",
    "facebook":  "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter":   "https://www.twitter.com",
    "github":    "https://www.github.com",
    "whatsapp":  "https://web.whatsapp.com",
    "netflix":   "https://www.netflix.com",
    "chatgpt":   "https://chat.openai.com",
    "linkedin":  "https://www.linkedin.com",
    "wikipedia": "https://www.wikipedia.org",
    "reddit":    "https://www.reddit.com",
    "amazon":    "https://www.amazon.in",
    "spotify":   "https://open.spotify.com",
}

APPS = {
    "chrome":        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad":       "notepad.exe",
    "calculator":    "calc.exe",
    "paint":         "mspaint.exe",
    "file explorer": "explorer.exe",
    "task manager":  "taskmgr.exe",
    "vs code":       r"C:\Users\NITHYAANATHAN\AppData\Local\Programs\Microsoft VS Code\Code.exe",
}

def handle_open(command):
    for name, url in WEBSITES.items():
        if name in command:
            speak(f"Opening {name}.")
            webbrowser.open(url)
            return
    for name, path in APPS.items():
        if name in command:
            speak(f"Opening {name}.")
            try:
                subprocess.Popen(path)
            except FileNotFoundError:
                speak(f"Couldn't find {name} on your PC.")
            return
    speak("I don't know how to open that.")

# ── GOOGLE SEARCH ─────────────────────────────────────────────────────────────
def handle_search(command):
    match = re.search(r"search (?:for |about )?(.+)", command)
    if match:
        query = match.group(1).strip()
        speak(f"Searching Google for {query}.")
        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    else:
        speak("What would you like me to search for?")

# ── JOKES ─────────────────────────────────────────────────────────────────────
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the computer go to the doctor? Because it had a virus!",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why was the math book sad? It had too many problems.",
    "What do you call a fish without eyes? A fsh!",
    "Why don't scientists trust atoms? Because they make up everything!",
    "I asked Siri why I'm still single. She opened the front camera.",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What do you call fake spaghetti? An impasta!",
    "Why can't your nose be 12 inches long? Because then it would be a foot!",
    "I'm reading a book about anti-gravity. It's impossible to put down!",
    "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
]

def handle_joke():
    speak(random.choice(JOKES))

# ── MOTIVATIONAL QUOTES ───────────────────────────────────────────────────────
QUOTES = [
    "Believe you can and you're halfway there. — Theodore Roosevelt",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "It does not matter how slowly you go as long as you do not stop. — Confucius",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
    "The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
    "You are braver than you believe, stronger than you seem, and smarter than you think. — A.A. Milne",
    "Act as if what you do makes a difference. It does. — William James",
    "Start where you are. Use what you have. Do what you can. — Arthur Ashe",
    "Dream big and dare to fail. — Norman Vaughan",
]

def handle_quote():
    speak(random.choice(QUOTES))

# ── VOLUME CONTROL ────────────────────────────────────────────────────────────
def handle_volume(command):
    try:
        if "mute" in command:
            subprocess.run(["powershell", "-c",
                "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"], 
                capture_output=True)
            speak("Muted.")
        elif "unmute" in command:
            subprocess.run(["powershell", "-c",
                "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"], 
                capture_output=True)
            speak("Unmuted.")
        elif "increase" in command or "up" in command or "louder" in command:
            for _ in range(5):
                subprocess.run(["powershell", "-c",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"], 
                    capture_output=True)
            speak("Volume increased.")
        elif "decrease" in command or "down" in command or "lower" in command or "quieter" in command:
            for _ in range(5):
                subprocess.run(["powershell", "-c",
                    "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"], 
                    capture_output=True)
            speak("Volume decreased.")
        else:
            speak("Say increase volume, decrease volume, mute, or unmute.")
    except Exception as e:
        speak(f"Volume control error: {e}")

# ── NEWS ──────────────────────────────────────────────────────────────────────
def handle_news():
    if not HAS_REQUESTS:
        speak("Requests library not installed."); return
    if NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
        speak("No News API key set. Get a free one from newsapi.org. Opening it for you.")
        webbrowser.open("https://newsapi.org")
        return
    try:
        resp = requests.get(
            f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}&pageSize=5",
            timeout=6)
        if resp.status_code == 200:
            articles = resp.json().get("articles", [])
            if articles:
                speak(f"Here are the top {len(articles)} headlines.")
                for i, a in enumerate(articles, 1):
                    speak(f"{i}. {a['title']}")
            else:
                speak("No news found.")
        else:
            speak("Couldn't fetch news right now.")
    except Exception as e:
        speak(f"News error: {e}")

# ── SYSTEM INFO ───────────────────────────────────────────────────────────────
def handle_system(command):
    try:
        import psutil
        if "battery" in command:
            battery = psutil.sensors_battery()
            if battery:
                speak(f"Battery is at {battery.percent:.0f} percent. "
                      f"{'Charging.' if battery.power_plugged else 'Not charging.'}")
            else:
                speak("No battery found. You might be on a desktop.")
        elif "ram" in command or "memory" in command:
            mem = psutil.virtual_memory()
            speak(f"RAM usage is {mem.percent:.0f} percent. "
                  f"{mem.available // (1024**3)} GB available.")
        elif "cpu" in command or "processor" in command:
            cpu = psutil.cpu_percent(interval=1)
            speak(f"CPU usage is {cpu:.0f} percent.")
        elif "disk" in command or "storage" in command:
            disk = psutil.disk_usage('/')
            speak(f"Disk usage is {disk.percent:.0f} percent. "
                  f"{disk.free // (1024**3)} GB free.")
        else:
            speak("I can check battery, RAM, CPU, or disk. Which one?")
    except ImportError:
        speak("psutil not installed. Run: pip install psutil")
    except Exception as e:
        speak(f"System info error: {e}")

# ── REMINDERS ─────────────────────────────────────────────────────────────────
def _load_reminders():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE) as f:
            return json.load(f)
    return []

def _save_reminders(reminders):
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2)

def handle_set_reminder(command):
    match = re.search(
        r"(?:remind me to|remind me|set reminder)(.*?)in (\d+)\s*(minute|minutes|hour|hours)",
        command)
    if not match:
        speak("Try: remind me to call mom in 10 minutes."); return
    label   = match.group(1).strip() or "your reminder"
    amount  = int(match.group(2))
    unit    = match.group(3)
    seconds = amount * (60 if "minute" in unit else 3600)
    fire_at = (datetime.datetime.now() + datetime.timedelta(seconds=seconds)).isoformat()
    reminders = _load_reminders()
    reminders.append({"label": label, "fire_at": fire_at, "seconds": seconds})
    _save_reminders(reminders)
    speak(f"Reminder set: {label} in {amount} {unit}.")
    def _fire():
        time.sleep(seconds)
        speak(f"Reminder: {label}!")
    threading.Thread(target=_fire, daemon=True).start()

def handle_list_reminders():
    now = datetime.datetime.now()
    active = [r for r in _load_reminders()
              if datetime.datetime.fromisoformat(r["fire_at"]) > now]
    if not active:
        speak("No active reminders.")
    else:
        speak(f"You have {len(active)} reminder(s).")
        for r in active:
            diff = int((datetime.datetime.fromisoformat(r["fire_at"]) - now).total_seconds() / 60)
            speak(f"{r['label']} in about {diff} minutes.")

# ── HELP ──────────────────────────────────────────────────────────────────────
def handle_help():
    speak(
        "Here's what I can do: "
        "time, date, weather, "
        "open YouTube or any app, "
        "search for anything on Google, "
        "tell me a joke, motivate me, "
        "increase or decrease volume, mute, "
        "latest news, "
        "battery level, RAM usage, CPU usage, "
        "set a reminder, list reminders, "
        "or say goodbye to shut me down."
    )

# ── COMMAND ROUTER ────────────────────────────────────────────────────────────
def route(command: str) -> bool:
    if not command:
        return True
    if any(w in command for w in ("goodbye", "shut down", "bye jarvis", "stop jarvis", "exit")):
        speak("Goodbye! Say Hey Jarvis anytime to wake me up.")
        return False

    if "help" in command:
        handle_help()
    elif "time" in command:
        handle_time()
    elif "date" in command:
        handle_date()
    elif "weather" in command:
        handle_weather(command)
    elif "search" in command:
        handle_search(command)
    elif any(w in command for w in ("joke", "funny", "laugh")):
        handle_joke()
    elif any(w in command for w in ("motivate", "quote", "inspiration")):
        handle_quote()
    elif any(w in command for w in ("volume", "mute", "unmute", "louder", "quieter")):
        handle_volume(command)
    elif any(w in command for w in ("news", "headlines")):
        handle_news()
    elif any(w in command for w in ("battery", "ram", "memory", "cpu", "disk", "storage", "processor")):
        handle_system(command)
    elif "list reminder" in command or "my reminder" in command:
        handle_list_reminders()
    elif any(w in command for w in ("remind", "set reminder")):
        handle_set_reminder(command)
    elif any(w in command for w in ("open", "launch", "start")):
        handle_open(command)
    else:
        speak("I didn't catch that. Say help for a list of things I can do.")
    return True

# ── WAKE WORD LOOP ────────────────────────────────────────────────────────────
def contains_wake_word(text):
    if text is None:
        return False
    return any(w in text for w in WAKE_WORDS)

def main():
    print("=" * 55)
    print("  🤖  JARVIS  —  Always-On Voice Assistant")
    print("  Say 'Hey Jarvis' to wake me up")
    print("  Say 'goodbye' to exit")
    print("=" * 55)

    if "--text" in sys.argv:
        speak("Jarvis text mode ready.")
        print("  Running in TEXT mode.\n")
        while True:
            try:
                command = input("  You > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break
            if not route(command):
                break
        return

    recognizer = build_recognizer()
    try:
        mic = sr.Microphone()
    except Exception:
        print("\n❌  Microphone not found. Run with --text flag.\n")
        sys.exit(1)

    print("\n  Calibrating microphone …", end=" ", flush=True)
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("done.")

    speak("Jarvis is ready. Say Hey Jarvis to wake me up.")
    print("\n  😴 Sleeping … waiting for 'Hey Jarvis'\n")

    while True:
        text = listen_once(recognizer, mic, timeout=5, phrase_limit=4)
        if not contains_wake_word(text):
            continue

        print("  ⚡ Wake word detected!")
        speak("Yes?")

        print("  🎙️  Listening for command …", end=" ", flush=True)
        command = listen_once(recognizer, mic, timeout=6, phrase_limit=10)
        if command:
            print(f"Command: «{command}»")
            alive = route(command)
            if not alive:
                break
        else:
            speak("I didn't catch that. Say Hey Jarvis and try again.")

        print("\n  😴 Going back to sleep … say 'Hey Jarvis' to wake me\n")

if __name__ == "__main__":
    main()
