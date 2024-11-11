from datetime import datetime
import os
import csv


# Function to log a user's timetable with their sign-in, sign-out times, and total time into csv
def timetable(name, signedInTime, signedOutTime, totalTime):
    # Store the data in a list of dictionaries
    data = [
        {
            "name": name,
            "signedInTime": signedInTime,
            "signedOutTime": signedOutTime,
            "totalTime": totalTime,
        },
    ]

    # Open the CSV file in append mode to add new data
    with open("flask-app/data/history/timesheet.csv", "a", newline="") as csvfile:
        fieldnames = ["name", "signedInTime", "signedOutTime", "totalTime"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat("flask-app/data/history/timesheet.csv").st_size == 0:
            writer.writeheader()
        writer.writerows(data)
