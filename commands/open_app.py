import AppOpener

def open_application(app_name):
    try:
        AppOpener.open(app_name, match_closest=True)
        print(f"Opening {app_name}")
    except:
        print("App not found")