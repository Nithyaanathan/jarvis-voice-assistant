# 🎙️ Desktop Voice Assistant

A minimal Python voice assistant — no GUI needed, runs in your terminal.

---

## Features
| Say…                                    | Does…                              |
|-----------------------------------------|------------------------------------|
| "time" / "date"                         | Tells current time / date          |
| "weather" / "weather in Mumbai"         | Live weather via OpenWeatherMap    |
| "remind me to call mom in 10 minutes"   | Sets a timed reminder              |
| "list reminders"                        | Reads out active reminders         |
| "help"                                  | Lists all commands                 |
| "quit" / "exit"                         | Stops the assistant                |

---

## Setup

### 1 — Install system dependencies

**Ubuntu / Debian**
```bash
sudo apt update
sudo apt install -y python3-pyaudio portaudio19-dev espeak
```

**macOS**
```bash
brew install portaudio
```

**Windows** — PyAudio needs a pre-built wheel; run:
```bash
pip install pipwin
pipwin install pyaudio
```

### 2 — Install Python packages
```bash
pip install -r requirements.txt
```

### 3 — Add your OpenWeather API key *(optional)*
1. Sign up free at https://openweathermap.org/api
2. Open `assistant.py` and replace `YOUR_API_KEY_HERE` with your key.
3. Optionally change `DEFAULT_CITY` to your city.

### 4 — Run

**Voice mode** (needs microphone)
```bash
python assistant.py
```

**Text mode** (no microphone — great for testing)
```bash
python assistant.py --text
```

---

## Project layout
```
voice_assistant/
├── assistant.py        ← main script (single file, fully self-contained)
├── requirements.txt    ← pip dependencies
├── reminders.json      ← created automatically when you set reminders
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No microphone found` | Use `--text` mode or check device settings |
| `ALSA / PortAudio errors` | Install `portaudio19-dev` (Linux) or `portaudio` (macOS) |
| Recognition never understands | Speak clearly; adjust `energy_threshold` in the script |
| Weather always fails | Check your API key and that `requests` is installed |
| TTS silent on Linux | Install `espeak`: `sudo apt install espeak` |
