# Google Calendar API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Date utils
import datetime
import calendar
import pytz

# OS
import os.path

# Arg parser
import argparse

# Style and look
import colorama
from colorama import Fore, Back, Style






def color(string, fore, style="normal"):
    fore_colors = {"light_yellow" : Fore.LIGHTYELLOW_EX,
                   "light_cyan"   : Fore.LIGHTCYAN_EX,
                   "light_white"  : Fore.LIGHTWHITE_EX,
                   "light_red"    : Fore.LIGHTRED_EX,
                   "light_green"  : Fore.LIGHTGREEN_EX,
                    }
    styles = {"bright" : Style.BRIGHT,
              "normal" : Style.NORMAL}

    return fore_colors[fore] + styles[style] + string + Fore.RESET

class gcalendar_fetcher:
    service = None
    offset = None

    def __init__(self, service):
        self.service = service 

        # Get timezone from the calendar
        calendar_timezone = service.calendars().get(calendarId="primary").execute()["timeZone"]
        
        # Get utc offset
        local_timezone = pytz.timezone(calendar_timezone)
        aware = local_timezone.localize(datetime.datetime.now())
        self.offset = aware.utcoffset()
        #print(type(localtz))
        #print(offset, type(offset))
        colorama.init(autoreset=True)   # Colors resets after each print

    def show_events(self, date):

        date_day = datetime.datetime(year = date.year,
                                month = date.month,
                                day = date.day,
                                ) - self.offset   # Subtract time zone offset
                                #)
        #print(date_day, self.offset)
        date_post_day = date_day + datetime.timedelta(days = 1) # gets tomorrow
        
        # Create today and tomorrow in iso format for list argument
        date_day_iso = date_day.isoformat() + 'Z'
        date_post_day_iso = date_post_day.isoformat() + 'Z'

        # Gets all event between date_day and tomorrow
        events_result = self.service.events().list(calendarId = "primary",
                                            timeMin = date_day_iso,
                                            timeMax = date_post_day_iso,
                                            singleEvents=True,
                                            orderBy='startTime').execute()
        # List of events in the calendar
        events = events_result.get('items', [])

        if not events:
            print(color("No upcoming events found at " + calendar.day_name[date_post_day.weekday()] + " " + str(date)[0:10], "light_green", "bright"))
            return

        # Display red title
        print(color("Events at " + calendar.day_name[date.weekday()] + " " + str(date)[0:10], "light_red", "bright"))
        for event in events:

            # ---------- Get time info ----------
            # event["start"] contains "dateTime" key only if the event is NOT the whole day therefore has start time and end time
            if "dateTime" in event["start"].keys():

                TIME_LOWERBOUND_IN_STRING = 11
                TIME_UPPERBOUND_IN_STRING = 16
                start_time = event["start"].get("dateTime")[TIME_LOWERBOUND_IN_STRING:TIME_UPPERBOUND_IN_STRING]
                end_time = event["end"].get("dateTime")[TIME_LOWERBOUND_IN_STRING:TIME_UPPERBOUND_IN_STRING]
                time_interval = "[" + start_time + ", " + end_time + "]"
                missing_days = self.get_missing_days(event["start"]["dateTime"])
            # event["start"] contains "date" key only if the event is the whole day
            elif "date" in event["start"].keys():

                time_interval = "[Whole day]"
                missing_days = self.get_missing_days(event["start"]["date"])
            else:
                time_interval = "[Error retrieving time interval]"

            # ---------- Get missing days info ----------
            missing_days_string = color("(Today)", "light_red", "bright") if missing_days == 0 else "(in " + str(missing_days) + " days)"
            
            # ---------- Get location info ----------
            if "location" in event.keys():
                location = event["location"]
                location_string = "at " + color(location, "light_cyan")
                #print(" at " + color(location, "light_cyan"), end="")
            else:
                location_string = ""

            # ---------- Print event info ----------
            print("*", color(event["summary"], "light_yellow"), ":", time_interval, location_string, missing_days_string, end="\n", sep=" ")

    def show_today_events(self):

        self.show_events(datetime.datetime.utcnow())
        return

    def show_tomorrow_events(self):
        
        one_day = datetime.timedelta(days=1)
        self.show_events(datetime.datetime.utcnow() + one_day)
        return

    def show_next_days_events(self, days):

        for i in range(0, days):
            # Each iteration it invokes the show_events method adding one day
            self.show_events(datetime.datetime.utcnow() + datetime.timedelta(days=i))

    def show_week_events(self):

        day = datetime.datetime.utcnow()

        while True:
            self.show_events(day)   # show events
            day += datetime.timedelta(days=1)   # adds one day

            if day.weekday() == 0:  # If the next day is monday then break
                break

    def show_all_birthdays(self):

        # Gets all Caledars info
        # calendars_id = self.service.calendarList().list().execute()["items"]
        # for c in calendars_id:
        #    print(c, "\n\n")


        date = datetime.datetime.now()
        date_day = datetime.datetime(year = date.year,
                                    month = date.month,
                                    day = date.day,
                                ) - self.offset   # Subtract time zone offset
        date_year_later = date_day + datetime.timedelta(days=365) # gets one year later
        
        # Create the dates in iso format for list argument
        date_day_iso = date_day.isoformat() + 'Z'
        date_year_later_iso = date_year_later.isoformat() + 'Z'

        # Gets all event between now and one year apart in birthday calendar
        events_result = self.service.events().list(calendarId = "addressbook#contacts@group.v.calendar.google.com",
                                            timeMin = date_day_iso,
                                            timeMax = date_year_later_iso,
                                            singleEvents=True,
                                            orderBy='startTime').execute()


        event_list = events_result.get("items", [])

        for event in event_list:
            #print(event, "\n\n")
            full_name = event["gadget"]["preferences"]["goo.contactsFullName"]
            
            date = event["start"]["date"]            
            missing_days = self.get_missing_days(event["start"]["date"])
            missing_days_string = color("(Today)", "light_red", "bright") if missing_days == 0 else "(in " + str(missing_days) + " days)"

            print("*", color(full_name, "light_yellow"), "on", color(date, "light_cyan"), missing_days_string)
            
    def get_missing_days(self, date_string):
        YYYY_MM_DD_STRING_LENGHT = 10
        date = date_string[0:YYYY_MM_DD_STRING_LENGHT]
        # split date separating tokens with - and cast them to integer type
        year, month, day = [int(x) for x in date.split("-")] 
        # get difference in days
        delta = datetime.date(year, month, day) - datetime.date.today()
        return delta.days



def main():

    parser = argparse.ArgumentParser(description="Google Calendar Util via CLI.")
    parser.add_argument("-t", action="store_true", help="Show today events.")
    parser.add_argument("--today", action="store_true", help="Show today events.")
    parser.add_argument("--tomorrow", action="store_true", help="Show tomorrow events.")
    parser.add_argument("-tm", action="store_true", help="Show tomorrow events.")
    # args.d's type is datetime.datetime
    parser.add_argument("-d", type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d'), help="Date in the format YYYY-MM-DD.")
    parser.add_argument("-b", action="store_true", help="Show all birthdays from now to an year.")
    parser.add_argument("-n", type=int, help="Show events for the next n days.")
    parser.add_argument("--next", type=int, help="Show events for the next n days.")
    parser.add_argument("-w", action="store_true", help="Show all events of the remaining week days, today included.")

    args = parser.parse_args()

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None

    # -------------------- Get directory info --------------------
    dir_path = os.path.dirname(os.path.realpath(__file__))
    credentials_file = os.path.join(dir_path, "credentials.json")
    token_path = os.path.join(dir_path, "token.json")

    # -------------------- Get Credentials --------------------
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
            except FileNotFoundError as fnfe:
                print("File credentials.json not found.")
                print("Follow Prerequisites at https://developers.google.com/calendar/api/quickstart/python.")
                print("Put the credentials.json file in", credentials_file)
                exit()
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    

    try:

        service = build("calendar", "v3", credentials=creds)
        fetcher = gcalendar_fetcher(service=service)
        
        if (args.t or args.today):
            fetcher.show_today_events()
        
        if (args.d):
            fetcher.show_events(args.d)

        if (args.tomorrow or args.tm):
            fetcher.show_tomorrow_events()

        if (args.n or args.next):
            fetcher.show_next_days_events(args.n)

        if (args.w):
            fetcher.show_week_events()

        if (args.b):
            fetcher.show_all_birthdays()
            

        

    except HttpError as http_error:
        print('An error occurred: %s' % http_error)


if __name__ == '__main__':
    main()