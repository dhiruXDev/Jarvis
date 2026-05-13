# pyrefly: ignore [missing-import]
import speedtest
import subprocess

def check_internet_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        ping = st.results.ping
        download = st.download()/1_000_000
        upload = st.upload()/1_000_000
        return {
            "download": round(download, 2),
            "upload": round(upload, 2)
        }
    except Exception as e:
        return f"Error: {e}"

# ping google
def ping_google():
    try:
        result = subprocess.run("ping google.com", shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"