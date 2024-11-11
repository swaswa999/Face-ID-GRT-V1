import face_recognition
import pickle
import os

# Path where known face encodings are stored
KNOWN_FACE_PATH = "flask-app/data/known_faces.pkl"

# Tolerance value for comparing face encodings. Lower values mean stricter matching
TOLERANCE = 0.38


# This Function is for saving the encodings for a person into a file (ready to be used)
# This is so we can acsese them faster rather than loading each imiage for every comparition, then compute it then compare
# Makes actualy comparition more faster to loop though
# As instead of looking at the Exact same img and encoding it every time, we just save the encodings
def save_known_face_encoding(image_path, name):
    # Load the image and get the face encoding
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]

    # Creating a blank list to later store known encodings with corrisponding name
    known_faces = []

    if os.path.exists(
        KNOWN_FACE_PATH
    ):  # incase project file is moved around, make sure that
        with open(KNOWN_FACE_PATH, "rb") as f:
            # Load the previously saved face encodings
            loded_data = pickle.load(f)
            if isinstance(loded_data, list):
                known_faces = loded_data  # If it's a list, use it as known faces
            else:
                known_faces = [loded_data]  # else, wrap it in a list

    # Append the new face encoding along with the name
    known_faces.append((encoding, name))

    # Save the updated list of known faces
    with open(KNOWN_FACE_PATH, "wb") as f:
        pickle.dump(known_faces, f)

    print(f"Encoded and saved face for {name}")  # REMOVE WHEN DONE


# This functions job is to take the newly created pkl file and save it into our server (or comp) memmory
# basically making it ready to be used, it will return a list with face names and its encoding


def load_known_face_encodings():
    if os.path.exists(KNOWN_FACE_PATH):
        with open(KNOWN_FACE_PATH, "rb") as f:
            # Load the face encodings from the file
            loded_data = pickle.load(f)
            if isinstance(loded_data, list):
                return loded_data  # Return the list of known faces
            else:
                return [loded_data]  # Return as a list if it's not a list already
    return []  # Return an empty list if no known faces file exists


# This is the last function and it is for actually comparing the photo the user just took with the encoded photo
# We are also encoding the image the user just gave us so we can compare
# Then we are returning the name of who our system thinks this is
# problem with this is, with similar facial fetures it is sometimes hard to distinguishable depending on lighting
def compare_face_to_known_image():
    # Path to the image we want to compare
    comparison_image_path = "flask-app/data/captured_image.jpg"

    # Load known faces from the file
    known_faces = load_known_face_encodings()
    if not known_faces:
        print("No known face encodings found. Please save a known face encoding first.")
        return

    # Load the image we want to compare to known faces
    comparison_image = face_recognition.load_image_file(comparison_image_path)
    comparison_encodings = face_recognition.face_encodings(comparison_image)

    # Compare current face encoding  with the known faces
    for comparison_encoding in comparison_encodings:
        for known_encoding, known_name in known_faces:
            # Compare faces with in mind tolerance and check if they meet requirements
            # tolerance is the amount of sway between each face, this is because no matter what 2 photos will NEVER be the same
            match = face_recognition.compare_faces(
                [known_encoding], comparison_encoding, tolerance=TOLERANCE
            )[0]
            if match:
                # If person found, return the name of said person
                print(f"Match found: {known_name}")
                return known_name

    # If no match is found, return no match
    print("No matching face found.")  # REMOVE
    return "NoKnowface"


# Read the names from a file and save their face encodings
with open("flask-app/data/names.txt", "r") as file:
    # Create a list of names from the file, removing extra spaces
    names = [line.strip() for line in file if line.strip()]

# For each name, save their face encoding
for name in names:
    image_path = f"flask-app/data/face/{name}.jpg"
    save_known_face_encoding(image_path, name)
