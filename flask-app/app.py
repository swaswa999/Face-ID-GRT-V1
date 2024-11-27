# Import necessary libraries for Flask, computer vision, and file handling
from flask import Flask, render_template, Response, redirect, url_for
import cv2
from timetable import timetable
from faceCheck import compare_face_to_known_image
import os
from datetime import datetime
import csv

# Read the names from the file and store them in a list
with open("flask-app/data/names.txt", "r") as file:
    names = [line.strip() for line in file if line.strip()]

# TEMP MEMORY to track who's signed in or out
signedInTrack = {name: False for name in names}
signedInTime = {name: None for name in names}
signedOutTime = {name: None for name in names}


# Store the current user's name and check-in time
nameCurrent = ""
checkInTime = ""

# Initialize Flask app
app = Flask(__name__)

# Initialize the camera
camera = cv2.VideoCapture(0)


# Homepage route
@app.route("/")
def index():
    return render_template("index.html")


# Admin page route
@app.route("/admin")
def admin():
    data = []

    with open("flask-app/data/history/timesheet.csv", newline="") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        data = [row for row in reader]

    return render_template("admin.html", header=header, data=data)


# Function to stream video feed from the camera
def generate_video_feed():
    while True:
        # Capture frame (success is a boolean and frame is the photo)
        success, frame = camera.read()  # Capture frame
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)  # turn photo to save as JPG
        frame = buffer.tobytes()  # Convert to bytes
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )  # sends each frame as part of a video stream


# Video feed route for displaying camera stream
@app.route("/video_feed")
def video_feed():
    return Response(
        # multipart/x-mixed-replace lets us send frames without reloading
        # boundary is so computer knows start and end for video
        generate_video_feed(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# Route for the signed-in page
@app.route("/signedIn")
def signedIn():
    return render_template(
        "signedIn.html", nameCurrent=nameCurrent, checkInTime=signedInTime[nameCurrent]
    )


# Route for the signed-out page
@app.route("/signedOut")
def signedOut():
    # Calculate total time in minutes (MILITARY TIME)
    totalTime = (
        datetime.strptime(signedOutTime[nameCurrent], "%Y-%m-%d %H:%M")
        - datetime.strptime(signedInTime[nameCurrent], "%Y-%m-%d %H:%M")
    ).total_seconds() / 60

    # Log the timetable
    timetable(
        nameCurrent, signedInTime[nameCurrent], signedOutTime[nameCurrent], totalTime
    )

    return render_template(
        "signedOut.html",
        nameCurrent=nameCurrent,
        checkInTime=signedInTime[nameCurrent],
        checkOutTime=signedOutTime[nameCurrent],
        totalTime=totalTime,
    )


# Route for capturing a frame and processing the face
@app.route("/capture_frame", methods=["POST"])
def capture_frame():
    global nameCurrent
    success, frame = camera.read()  # Capture frame from the camera
    if success:
        cv2.imwrite(
            "flask-app/data/captured_image.jpg", frame
        )  # Save the frame as an image
        name = compare_face_to_known_image()  # Compare face to known images
        if name == "NoKnowface":  # If no known face is detected, try again
            return redirect(url_for("tryAgain"))

        nameCurrent = name
        if signedInTrack[name] == False:  # If not signed in, sign in the person
            signedInTrack[name] = True
            signedInTime[name] = datetime.now().strftime("%Y-%m-%d %H:%M")

            return redirect(url_for("signedIn"))

        if signedInTrack[name] == True:  # If already signed in, sign out the person
            signedInTrack[name] = False
            signedOutTime[name] = datetime.now().strftime("%Y-%m-%d %H:%M")

            return redirect(url_for("signedOut"))
    return redirect(url_for("error"))  # If something goes wrong, show an error page


# Error page route
@app.route("/error")
def error():
    return render_template("error.html")


# Try again page route
@app.route("/tryAgain")
def tryAgain():
    return render_template("tryAgain.html")


if __name__ == "__main__":
    import os

    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(host=host, port=port, debug=False)
