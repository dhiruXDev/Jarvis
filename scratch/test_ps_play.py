import asyncio
import edge_tts
import subprocess
import os
import time

async def main():
    text = "Testing PowerShell audio playback."
    voice = "en-US-GuyNeural"
    output_file = os.path.abspath("test_ps.mp3")
    
    print("Synthesizing...")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print("Synthesized.")
    
    if os.path.exists(output_file):
        print("Playing via PowerShell...")
        # Escape single quotes in path if any
        safe_path = output_file.replace("'", "''")
        cmd = f'''powershell -c "Add-Type -AssemblyName presentationcore; $player = New-Object System.Windows.Media.MediaPlayer; $player.Open('{safe_path}'); $player.Play(); while ($player.NaturalDuration.HasTimeSpan -eq $false) {{ Start-Sleep -Milliseconds 10 }}; Start-Sleep -Milliseconds ($player.NaturalDuration.TimeSpan.TotalMilliseconds + 200)"'''
        
        start_time = time.time()
        subprocess.run(cmd, shell=True)
        print(f"Playback took: {time.time() - start_time:.2f} seconds")
        
        try:
            os.remove(output_file)
            print("Cleanup complete.")
        except Exception as e:
            print("Cleanup error:", e)

if __name__ == "__main__":
    asyncio.run(main())
