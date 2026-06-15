import os
import time
import hashlib
import asyncio
import threading
from queue import Queue
from threading import Thread, Event
import subprocess
import sys
# pyrefly: ignore [missing-import]
from langdetect import detect
import builtins

from config.settings import VOICE_MAP

# Shared states
speech_queue = Queue()
is_speaking = Event()
t_worker = None
t_worker_lock = threading.Lock()

# Ensure cache directory exists
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "speech_cache"))
os.makedirs(CACHE_DIR, exist_ok=True)

async def _synthesize_edge_tts(text, voice, filepath):
    # pyrefly: ignore [missing-import]
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)

def _speak_sapi_fallback(text):
    """Local offline SAPI5 speech fallback in case edge-tts fails completely."""
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 1
        speaker.Speak(text)
    except Exception as sapi_err:
        print(f"[SPEAKER WORKER FALLBACK ERROR] SAPI failed: {sapi_err}")

def _play_audio_ps(filepath):
    """Plays MP3 invisibly using PowerShell and presentationcore MediaPlayer."""
    try:
        safe_path = filepath.replace("'", "''")
        cmd = f'''powershell -windowstyle hidden -c "Add-Type -AssemblyName presentationcore; $player = New-Object System.Windows.Media.MediaPlayer; $player.Open('{safe_path}'); $player.Play(); while ($player.NaturalDuration.HasTimeSpan -eq $false) {{ Start-Sleep -Milliseconds 10 }}; Start-Sleep -Milliseconds ($player.NaturalDuration.TimeSpan.TotalMilliseconds + 200)"'''
        
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            
        subprocess.run(cmd, shell=True, startupinfo=startupinfo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"[SPEAKER WORKER] PowerShell playback error: {e}")
        return False

def _speak_worker():
    from core.server import set_hud_status
    
    while True:
        try:
            text = speech_queue.get()
            if text is None:  # stop signal
                break
                
            clean_text = text.strip()
            if not clean_text:
                continue
                
            print(f"[SPEAKER WORKER] Processing text: '{clean_text}'")
            
            # 1. Detect response language
            try:
                lang = detect(clean_text)
            except Exception:
                lang = "en"
                
            # Determine appropriate voice and text to speak
            voice_key = "en"
            speak_text = clean_text
            
            if lang == "hi" or "hi" in lang:
                voice_key = "hi"
            elif lang == "pa" or "pa" in lang:
                voice_key = "hi"  # Fallback to Hindi voice for Punjabi
                try:
                    # Translate Gurmukhi script to Devanagari/Hindi so the neural voice can read it
                    # pyrefly: ignore [missing-import]
                    from deep_translator import GoogleTranslator
                    speak_text = GoogleTranslator(source="pa", target="hi").translate(clean_text)
                    print(f"[SPEAKER WORKER] Translated Punjabi to Hindi for voice: '{speak_text}'")
                except Exception as trans_err:
                    print(f"[SPEAKER WORKER] Punjabi translation failed: {trans_err}")
                    speak_text = clean_text
                
            voice = VOICE_MAP.get(voice_key, VOICE_MAP["en"])
            print(f"[SPEAKER WORKER] Language: {lang} (speaking as {voice_key}) -> using voice: {voice}")
            
            # 2. Setup cache path (hashed on the actual spoken text to support caching of translation)
            hash_val = hashlib.md5(f"{speak_text}_{voice}".encode('utf-8')).hexdigest()
            filepath = os.path.join(CACHE_DIR, f"{hash_val}.mp3")
            
            # 3. Synthesize if not cached
            success = True
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    asyncio.run(_synthesize_edge_tts(speak_text, voice, filepath))
                except Exception as synth_err:
                    print(f"[SPEAKER WORKER ERROR] Edge TTS synthesis failed for voice '{voice}': {synth_err}")
                    if os.path.exists(filepath):
                        try: os.remove(filepath)
                        except: pass
                    # Try English fallback voice
                    fallback_voice = VOICE_MAP.get("en", "en-US-GuyNeural")
                    print(f"[SPEAKER WORKER] Retrying synthesis with fallback voice '{fallback_voice}'...")
                    try:
                        hash_val_fb = hashlib.md5(f"{speak_text}_{fallback_voice}".encode('utf-8')).hexdigest()
                        filepath = os.path.join(CACHE_DIR, f"{hash_val_fb}.mp3")
                        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                            if os.path.exists(filepath):
                                os.remove(filepath)
                            asyncio.run(_synthesize_edge_tts(speak_text, fallback_voice, filepath))
                        success = True
                    except Exception as fb_err:
                        print(f"[SPEAKER WORKER ERROR] Fallback voice synthesis failed: {fb_err}")
                        if os.path.exists(filepath):
                            try: os.remove(filepath)
                            except: pass
                        success = False
            
            # 4. Play audio
            if success and os.path.exists(filepath):
                set_hud_status("speaking")
                is_speaking.set()
                
                play_ok = _play_audio_ps(filepath)
                
                if not play_ok:
                    # Fallback to SAPI
                    _speak_sapi_fallback(speak_text)
                    
                if speech_queue.empty():
                    is_speaking.clear()
                set_hud_status("idle")
            else:
                # Fallback to SAPI if edge-tts synthesis or file check failed completely
                set_hud_status("speaking")
                is_speaking.set()
                _speak_sapi_fallback(speak_text)
                if speech_queue.empty():
                    is_speaking.clear()
                set_hud_status("idle")
                    
        except Exception as queue_err:
            print(f"[SPEAKER WORKER ERROR] Worker queue error: {queue_err}")
            try:
                is_speaking.clear()
                set_hud_status("idle")
            except:
                pass

def speak(*args):
    global t_worker
    if t_worker is None:
        with t_worker_lock:
            if t_worker is None:
                t_worker = Thread(target=_speak_worker, daemon=True)
                t_worker.start()

    text = " ".join(str(arg) for arg in args)
    print("Jarvis:", text)
    speech_queue.put(text)

    # Broadcast Jarvis response bubble to the UI conversation feed
    from core.server import broadcast_event
    timestamp = time.strftime("%I:%M %p")
    broadcast_event("chat_message", {
        "sender": "Jarvis",
        "text": text,
        "timestamp": timestamp
    })

builtins.speak = speak
