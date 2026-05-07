    #Wish
import datetime
import time
def wish(self):
    hour = int(datetime.datetime.now().hour)
    t = time.strftime("%I:%M %p")
    day = self.Cal_day()
    print(t)
    if (hour>=0) and (hour <=12) and ('AM' in t):
        self.talk(f'Good morning boss, its {day} and the time is {t}')
    elif (hour >= 12) and (hour <= 16) and ('PM' in t):
        self.talk(f"good afternoon boss, its {day} and the time is {t}")
    else:
        self.talk(f"good evening boss, its {day} and the time is {t}")