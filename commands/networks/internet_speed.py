import speedtest
import subprocess
import threading 

def check_internet_speed():
    try:
        st = speedtest.Speedtest()

        st.get_best_server()

        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping

        result = (
            f"Download Speed: {round(download,2)} Mbps\n"
            f"Upload Speed: {round(upload,2)} Mbps\n"
            f"Ping: {round(ping,2)} ms"
        )

        print("\nJarvis:", result)

    except Exception as e:
        print("\nJarvis:", e)

def run_speed_test():
    print("Jarvis: Checking internet speed in background...")

    thread = threading.Thread(target=check_internet_speed)

    thread.start()
# ping google
def ping_google():
    try:
        result = subprocess.run("ping google.com", shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"