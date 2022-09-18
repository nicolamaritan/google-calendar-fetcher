# Google Calendar API
import string
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
            print(color("No upcoming events found at " + calendar.day_name[date.weekday()] + " " + str(date)[0:10], "light_green", "bright"))
            return

        # Display red title
        print(color("Events at " + calendar.day_name[date.weekday()] + " " + str(date)[0:10], "light_red", "bright"))
        for event in events:
            TIME_LOWERBOUND_IN_STRING = 11
            TIME_UPPERBOUND_IN_STRING = 16

            start_time = event["start"].get("dateTime")[TIME_LOWERBOUND_IN_STRING:TIME_UPPERBOUND_IN_STRING]
            end_time = event["end"].get("dateTime")[TIME_LOWERBOUND_IN_STRING:TIME_UPPERBOUND_IN_STRING]
            
            time_interval = "[" + start_time + ", " + end_time + "]"
            
            print("*", color(event["summary"], "light_yellow", "bright"), ":", time_interval, end="")
            
            # Tries to find a location: if not found it throws an exception
            try:
                location = event["location"]
                print(" at " + color(location, "light_cyan"), end="")
            except Exception as e:
                pass

            print("\n", end="") 

    def show_today_events(self):

        self.show_events(datetime.datetime.utcnow())
        return

    def show_tomorrow_events(self):
        
        one_day = datetime.timedelta(days=1)
        self.show_events(datetime.datetime.utcnow() + one_day)
        return


def main():

    parser = argparse.ArgumentParser(description="Google Calendar Util via CLI.")
    parser.add_argument("-t", action="store_true", help="Show today events.")
    parser.add_argument("--today", action="store_true", help="Show today events.")
    parser.add_argument("--tomorrow", action="store_true", help="Show tomorrow events.")
    # args.d's type is datetime.datetime
    parser.add_argument("-d", type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d'), help="Date in the format YYYY-MM-DD.")

    args = parser.parse_args()

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None

    # -------------------- Get Credentials --------------------
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    
    

    try:

        service = build("calendar", "v3", credentials=creds)
        fetcher = gcalendar_fetcher(service=service)
        
        if (args.t or args.today):
            fetcher.show_today_events()
        
        if (args.d):
            fetcher.show_events(args.d)

        if (args.tomorrow):
            fetcher.show_tomorrow_events()

        

    except HttpError as http_error:
        print('An error occurred: %s' % http_error)


if __name__ == '__main__':
    main()