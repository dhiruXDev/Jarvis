import sys
import time
from core.speaker import speak

print("Calling speak...")
speak("Hello, this is a test of the speaker system.")
print("Speak called. Waiting 5 seconds...")
time.sleep(5)
print("Done.")
