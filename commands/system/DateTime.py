import datetime
def current_time():

    try:

        now = datetime.now()

        return now.strftime("Time is %I:%M %p")

    except Exception as e:
        print(f"Time Error: {e}")
        return "Unable to get time"


def current_date():

    try:

        today = datetime.now()

        return today.strftime("Today's date is %d %B %Y")

    except Exception as e:
        print(f"Date Error: {e}")
        return "Unable to get date"
