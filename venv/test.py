from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import numpy as np
import pickle
import firebase_admin
from firebase_admin import credentials, db, storage
import face_recognition
from datetime import datetime

class AttendanceApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.imgBackground = cv2.imread('Resources/background.png')
        self.student_ids = []
        self.encode_list_known = []
        self.load_encoding_data()

        self.label = Label(text='Face Attendance System', size_hint=(1, 0.1))
        self.image = Image(size_hint=(1, 0.6))
        self.button = Button(text='Check In', size_hint=(1, 0.1))
        self.button.bind(on_press=self.check_in)

        self.modeType = 0
        self.counter = 0
        self.id = -1
        self.imgStudent = []

    def load_encoding_data(self):
        # Load student IDs and corresponding encodings from Firebase or local storage
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://face-attendance-af4c7-default-rtdb.firebaseio.com/",
            'storageBucket': "face-attendance-af4c7.appspot.com"
        })

        bucket = storage.bucket()
        blob = bucket.blob('EncodeFile.p')
        array = np.frombuffer(blob.download_as_string(), np.uint8)
        encodeListKnownWithIds = pickle.loads(array)
        self.encode_list_known, self.student_ids = encodeListKnownWithIds

    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        layout.add_widget(self.image)
        layout.add_widget(self.button)

        # Start the video capture and processing
        Clock.schedule_interval(self.update, 1.0 / 30.0)

        return layout

    def update(self, dt):
        success, img = self.cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        self.imgBackground[162:162 + 480, 55:55 + 640] = img

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(self.encode_list_known, encodeFace)
                faceDis = face_recognition.face_distance(self.encode_list_known, encodeFace)

                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    print("Known Face Detected")
                    print(self.student_ids[matchIndex])
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    self.imgBackground = cvzone.cornerRect(self.imgBackground, bbox, rt=0)
                    self.id = self.student_ids[matchIndex]
                    if self.counter == 0:
                        cvzone.putTextRect(self.imgBackground, "Loading", (275, 400))
                        self.counter = 1
                        self.modeType = 1

            if self.counter != 0:
                if self.counter == 1:
                    # Get the Data
                    studentInfo = db.reference(f'Students/{self.id}').get()
                    blob = storage.bucket().get_blob(f'Images/{self.id}.jpg')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    self.imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                    if secondsElapsed > 30:
                        ref = db.reference(f'Students/{self.id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        self.modeType = 3
                        self.counter = 0

                if self.modeType != 3:
                    if 10 < self.counter < 20:
                        self.modeType = 2

                    if self.counter <= 10:
                        cv2.putText(self.imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(self.imgBackground, str(studentInfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(self.imgBackground, str(self.id), (1050, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(self.imgBackground, str(studentInfo['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(self.imgBackground, str(studentInfo['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(self.imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(self.imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                        self.imgBackground[175:175 + 216, 909:909 + 216] = self.imgStudent

                    self.counter += 1

                    if self.counter >= 20:
                        self.counter = 0
                        self.modeType = 0
                        studentInfo = []
                        self.imgStudent = []

        else:
            self.modeType = 0
            self.counter = 0

        # Convert frame to texture for display in Kivy
        texture = self.convert_frame_to_texture(self.imgBackground)
        self.image.texture = texture

    def convert_frame_to_texture(self, frame):
        frame = cv2.flip(frame, 0)
        buf = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture

    def check_in(self, instance):
        # Implement attendance recording logic
        pass

if __name__ == '__main__':
    AttendanceApp().run()

