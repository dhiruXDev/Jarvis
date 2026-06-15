import sys
import os
import time

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.speaker import speak

def test():
    print("Enqueuing English response...")
    speak("Hello Boss, I am testing the new Edge text to speech system.")
    
    print("Enqueuing Hindi response...")
    speak("नमस्ते सर, मैं आपका सहायक जार्विस हूँ।")
    
    print("Enqueuing Punjabi response...")
    speak("ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਜੀ, ਮੈਂ ਤੁਹਾਡਾ ਸਹਾਇਕ ਜਾਰਵਿਸ ਹਾਂ।")
    
    # Wait for background thread to process and play
    print("Waiting for queue to play all items...")
    time.sleep(25)
    print("Test finished.")

if __name__ == "__main__":
    test()
