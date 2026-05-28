import requests
import csv
import pandas
import sys
from collections import deque
from datetime import timedelta, date
from urllib.parse import urlsplit, parse_qs

def get_length_sec(vid_link): # gets youtube video length (secs) via youtube-api
    video_id = parse_qs(urlsplit(vid_link).query).get('v')[0]

    json_data = {
        'context': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20260101.01.00',
            },
        },
        'videoId': video_id
    }

    response = requests.post('https://www.youtube.com/youtubei/v1/player', json=json_data)

    return int(response.json().get('videoDetails').get('lengthSeconds'))

def was_written_today(pands_csv): # checks if entry exists for the current date
    try:
        last_date = pands_csv.iloc[-1, input_csv.columns.get_loc('Date')]
    except IndexError:
        return False
    else:
        if last_date == str(date.today()):
            return True
        else:
            return False

def log_time(input_csv, was_logged): # logic for writing to csv with input times

    if was_written_today(input_csv) == False: # if no entry for today then make one
        with open("input_log.csv", "a",  newline='') as csvfile:
            csvfile.write(f"{current_date},{running_count}\n")
            was_logged = True
        print(f"Written - {current_date} - {timedelta(seconds=running_count)}") 
    elif was_written_today(input_csv) and was_logged: # if entry for today exists and a time was logged in the current session
        input_csv.iloc[-1, input_csv.columns.get_loc('Total Input')] = running_count
        input_csv.to_csv('input_log.csv', index=False)
        print(f"Updated - {current_date} - {timedelta(seconds=running_count)}")
    else: # if an entry for today exists and no earlier time was logged in current session
        old_time = int(input_csv.iloc[-1, input_csv.columns.get_loc('Total Input')])
        input_csv.iloc[-1, input_csv.columns.get_loc('Total Input')] = old_time + running_count
        input_csv.to_csv('input_log.csv', index=False)
        updated_time = timedelta(seconds=int(input_csv.iloc[-1, input_csv.columns.get_loc('Total Input')]))
        print(f"Sucessfully added to todays total time.\n{timedelta(seconds=old_time)} -> {updated_time}")

    return was_logged

def main():
    is_csv = False
    with open("input_log.csv", "a+",  newline='') as csvfile: # checks if CSV with Date and Input Time header exists, creates if not 
        csvfile.seek(0)
        reader = csv.reader(csvfile, delimiter=",")
        header = next(reader, False)

        if not header:
            csvfile.seek(0)
            csvfile.write('Date,Total Input\n')
        elif header == ['Date', 'Total Input']:
            is_csv = True
        else:
            print("Confirm CSV Data")
            sys.exit()
    return is_csv

if __name__ == "__main__":
    is_csv = main()
    running_count = 0
    was_logged = False
    current_date = date.today()
    today_time = 0
    
    if len(sys.argv) > 1 and (sys.argv[1] == "-t" or sys.argv[1] == "-time"): # returns only the most recent date in CSV
        with open("input_log.csv", "r",  newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            try:
                last_entry = deque(reader, maxlen=1)[0] # converts list to queue to pop first(last) item
                final_time = timedelta(seconds=(int(last_entry[1])))
                print(f"Last log:\n{date.today()} - {final_time}")
                sys.exit()
            except IndexError:
                print("Did the CSV corrupt? Cannot read final time.")
                sys.exit()
            except ValueError:
                print("Did the CSV corrupt? Cannot read final time.")
                sys.exit()

    with open("input_log.csv", "r",  newline='') as csvfile: # init the running time tracker for today
        reader = csv.reader(csvfile, delimiter=",")
        try:
            last_entry = deque(reader, maxlen=1)[0]
            today_time = int(last_entry[1])
        except IndexError:
            today_time = 0
        except ValueError:
            today_time = 0

    while True: # main program loop, takes either link or command input
        print("Enter (link/command): ")
        try:
            input_var = input()
        except KeyboardInterrupt:
            print("WARNING: Program quit without saving.")
            sys.exit()
        
        match input_var:
            case "log": # logs running time for session
                input_csv = pandas.read_csv('input_log.csv')
                was_logged = log_time(input_csv, was_logged)
            case "quit": # quits program after saving
                input_csv = pandas.read_csv('input_log.csv')
                was_logged = log_time(input_csv, was_logged)

                with open("input_log.csv", "r",  newline='') as csvfile: # Outputs the total time for the session and day
                    reader = csv.reader(csvfile, delimiter=",")
                    try:
                        last_entry = deque(reader, maxlen=1)[0]
                        session_time = timedelta(seconds=running_count)
                        final_time = timedelta(seconds=(int(last_entry[1])))
                        print(f"Saved sucessfully\nInput for session:\n{session_time}\nFinal input time for today:\n{date.today()} - {final_time}")
                    except IndexError:
                        print("Did the CSV corrupt? Cannot read final time.")

                sys.exit()
            case _: # takes link or bunk input
                try:
                    video_length = get_length_sec(input_var)
                except TypeError:
                    print("Not a valid input")
                else:
                    running_count += video_length
                    vid_time = timedelta(seconds=video_length)
                    
                    print(f"Current Video Length - {vid_time}")
                    print(f"Total Time for Today - \n{timedelta(seconds=running_count + today_time)}")