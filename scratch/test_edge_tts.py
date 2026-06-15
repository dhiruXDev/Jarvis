import asyncio
import edge_tts
import win32com.client
import time
import os

async def main():
    text = "Hey Boss, I am testing the new edge text to speech system."
    voice = "en-US-GuyNeural"
    output_file = "test_speech.mp3"
    
    print(f"Synthesizing: '{text}' using {voice}...")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print("Synthesis complete.")
    
    if os.path.exists(output_file):
        print("Playing audio using WMPlayer.OCX...")
        wmp = win32com.client.Dispatch("WMPlayer.OCX")
        wmp.settings.volume = 100
        wmp.URL = os.path.abspath(output_file)
        wmp.controls.play()
        
        # Wait for playback to finish
        timeout = 15
        start_time = time.time()
        # playState: 1 is Stopped, 2 is Paused, 3 is Playing, 6 is Buffering, 8 is MediaEnded
        while wmp.playState not in (1, 8) and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            
        print("Playback finished.")
        # Cleanup
        try:
            # wait a bit for file release
            wmp.close()
            time.sleep(0.5)
            os.remove(output_file)
            print("Cleanup complete.")
        except Exception as e:
            print("Cleanup error:", e)

if __name__ == "__main__":
    asyncio.run(main())
