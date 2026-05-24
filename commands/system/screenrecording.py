# pyrefly: ignore [missing-import]
import os
import system as sys 
import subprocess
import pyautogui
import time
import cv2
import numpy as np
import threading
from queue import Queue
from datetime import datetime

class ScreenRecorder:
    def __init__(self, output_folder="recordings"):
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = None
        self.recording = False
        self.recording_thread = None
        self.frame_queue = Queue()
        
    def _record(self):
        try:
            start_time = time.time()
            while self.recording or not self.frame_queue.empty():
                frame = self.frame_queue.get()
                if frame is None:  # Stop signal
                    break
                    
                self.out.write(frame)
                
                # Safety timeout
                if time.time() - start_time > 3600:  # 1 hour max
                    break
                    
        except Exception as e:
            speak(f"Recorder Error: {e}")
        finally:
            self.recording = False
            if self.out:
                self.out.release()
                self.out = None
            
            self.frame_queue.put(None)  # Signal consumer to exit
            
    def start(self):
        if self.recording:
            return "Already recording"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_folder, f"recording_{timestamp}.avi")
        
        try:
            # Get screen resolution dynamically
            screen = np.array(pyautogui.screenshot())
            height, width, layers = screen.shape
            
            self.out = cv2.VideoWriter(filename, self.fourcc, 15.0, (width, height))
            self.recording = True
            
            self.recording_thread = threading.Thread(target=self._record, daemon=True)
            self.recording_thread.start()
            
            return f"Recording started: {filename}"
            
        except Exception as e:
            speak(f"Start Error: {e}")
            return f"Failed to start recording: {e}"
            
    def stop(self):
        if not self.recording:
            return "Not recording"
            
        self.recording = False
        self.frame_queue.put(None)
        
        if self.recording_thread:
            self.recording_thread.join(timeout=5)
            
        return "Recording stopped"

    def is_recording(self):
        return self.recording

# Global instance (or can be managed by caller)
screen_recorder = ScreenRecorder()

def start_screen_recording():
    """Start screen recording for 1 minute (default for practical use)"""
    try:
        # For practical use, record for a limited time by default
        # Or can be extended with parameters
        
        result = screen_recorder.start()
        
        if "started" in str(result):
            # Auto-stop after 60 seconds for demo/practicality
            threading.Timer(60.0, stop_screen_recording).start()
            return "Screen recording started for 60 seconds"
        
        return result
        
    except Exception as e:
        speak(f"Error: {e}")
        return f"Failed to record screen: {e}"

def stop_screen_recording():
    """Stop screen recording"""
    try:
        return screen_recorder.stop()
    except Exception as e:
        speak(f"Error: {e}")
        return f"Failed to stop recording: {e}"

def check_screen_recording_status():
    """Check if screen recording is active"""
    if screen_recorder.is_recording():
        return "Screen recording is active"
    else:
        return "Screen recording is not active"

def open_screen_recordings_folder():
    """Open the folder containing screen recordings"""
    try:
        folder = os.path.abspath(screen_recorder.output_folder)
        
        # Open the folder using default file explorer
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":  # macOS
            subprocess.Popen(['open', folder])
        else:  # Linux
            subprocess.Popen(['xdg-open', folder])
            
        return f"Opened screen recordings folder: {folder}"
    except Exception as e:
        speak(f"Error opening folder: {e}")
        return f"Failed to open recordings folder: {e}"