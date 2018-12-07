import numpy as np
import face_recognition
import csv
import cv2
import time
import threading


# The class to store, restore and remove faces to database
# It can also detect, recognize multi faces and show labels
class FaceProcess:
    def __init__(self, resize_frame=0.25, recognize_threshold=0.4, detect_interval=3):

        # basic parameters
        self._resize = resize_frame         # Used to resize the frame to gain faster speed
        self._compare_threshold = recognize_threshold   # Used to recognized people
        self._detect_inter = detect_interval    # Set how many frame to detect once

        # stored data set
        self._cnt = 0                       # Used to cooperation with _detect_inter
        self._known_face_encodings = []     # Stores known face encodings
        self._known_face_names = []         # Stores known face names
        self._file_data = []                # Stores file data read from .csv file

        # detection results
        self._face_locations = []           # Stores face locations that been detected
        self._face_names = []               # Stores face names that been recognized


    # Save data to .csv file
    # def save_database(self, cap_scan):
    #     # Let the user to input the name
    #     # name = get_input("Input", "Please input your name:")
    #     name = "Bowen"
    #     if not name:
    #         self.saving = False
    #         return
    #
    #     # Open a camera
    #     cnt = 0
    #
    #     # Store "person_store_number" numbers encodings of the user to store_face_encodings
    #     data = []
    #     while True:
    #         ret, frame = cap_scan.read()
    #         small_frame = cv2.resize(frame, (0, 0), fx=self._resize, fy=self._resize)
    #         self._face_locations = face_recognition.face_locations(small_frame)
    #         face_encodings = face_recognition.face_encodings(small_frame, self._face_locations)
    #         if face_encodings:
    #             data.append(np.insert(np.array(face_encodings).astype(np.str), 0, name))
    #             cnt = cnt + 1
    #         if cnt >= self._person_store_number:
    #             break

        # # Decide which method should be used
        # data_store = data
        # if name in self._known_face_names:
        #     # Open the file and rewrite the content
        #     file = open(self._filename, 'w')
        #     for i in range(len(self._known_face_names)):
        #         if self._known_face_names[i] != name:
        #             tmp = np.insert(np.array(self._known_face_encodings[i]).astype(np.str),
        #                             0, self._known_face_names[i])
        #             data_store.append(tmp)
        # else:
        #     # Open the file to add content
        #     file = open(self._filename, 'a')
        #
        # # Write file
        # writer = csv.writer(file, delimiter=',', lineterminator='\n')
        # for content in data_store:
        #     writer.writerow(content)
        # file.close()
        #
        # # Reload data from file
        # self.load_database()
        #
        # # End the saving process
        # self.saving = False

    # Delete existing data with specific name
    def delete_data(self, filename):
        # name = get_input("Input", "Please input the name you want to delete:")
        name = "Bowen"
        if not name:
            return

        if name not in self._known_face_names:
            return

        # delete data
        data_store = []
        for i in range(len(self._known_face_names)):
            if self._known_face_names[i] != name:
                tmp = np.insert(np.array(self._known_face_encodings[i]).astype(np.str),
                                0, self._known_face_names[i])
                data_store.append(tmp)

        # Write file
        file = open(filename, 'w')
        writer = csv.writer(file, delimiter=',', lineterminator='\n')
        for content in data_store:
            writer.writerow(content)
        file.close()

        # Reload data from file
        self.load_database(filename)

    # Load faces data from .csv file
    def load_database(self, filename):
        file = open(filename, 'r')
        self._file_data = np.array(list(csv.reader(file, delimiter=',')))
        file.close()

        if self._file_data.shape[0] != 0:
            self._known_face_names = self._file_data[:, 0]
            self._known_face_encodings = []
            for i in range(self._file_data.shape[0]):
                self._known_face_encodings.append(self._file_data[i, 1:].astype(np.float))
        else:
            self._known_face_names = []
            self._known_face_encodings = []

    # Detect the faces in the frame and store them to _face_locations
    def detect_people(self, frame):
        self._cnt += 1
        if self._cnt > self._detect_inter:
            self._cnt = 0

            # resize the frame and convert the frame
            small_frame = cv2.resize(frame, (0, 0), fx=self._resize, fy=self._resize)

            # Find all the faces and face encodings in the current frame of video
            self._face_locations = face_recognition.face_locations(small_frame)

            # If _mode was set 1, recognize people with detect
            # self._recognize_people_core(small_frame)

    # recognize the people's identity
    def _recognize_people_core(self, frame):
        # Get the encodings of faces detected
        face_encodings = face_recognition.face_encodings(frame, self._face_locations)

        # Match with the database and store the names
        self._face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            name = "Unknown"
            matches = face_recognition.compare_faces(self._known_face_encodings, face_encoding,
                                                     self._compare_threshold)

            # If a match was found in known_face_encodings, use the most match one
            if True in matches:
                if len(matches) > 1:
                    face_distances = face_recognition.face_distance(self._known_face_encodings,
                                                                    face_encoding)
                    most_match_index = np.where(face_distances == min(face_distances))[0][0]
                    name = self._known_face_names[most_match_index]
                else:
                    first_match_index = matches.index(True)
                    name = self._known_face_names[first_match_index]

            # Add name to face_names
            self._face_names.append(name)

    # Display the result in the frame
    def get_detected_ans(self):
        # Reset the face_positions_percent
        face_positions_return = []
        # Transfer the results
        for i in range(len(self._face_locations)):
            # Scale back up face locations since the frame we detected
            top = int(self._face_locations[i][0] / self._resize)
            right = int(self._face_locations[i][1] / self._resize)
            bottom = int(self._face_locations[i][2] / self._resize)
            left = int(self._face_locations[i][3] / self._resize)

            face_positions_return.append([top,
                                         left,
                                         bottom,
                                         right])

        return self._face_names, face_positions_return

