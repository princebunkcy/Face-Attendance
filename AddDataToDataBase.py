import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://face-attendance-af4c7-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')
data = {
    "2838292":
        {
            "name": "Andy Roddick",
            "major": "Data Science",
            "starting_year": 2023,
            "total_attendance": 4,
            "standing": "G",
            "year": 1,
            "last_attendance_time": "2024-1-11 00:54:34"
        },
    "2225362":
        {
            "name": "Prince Onuekwa",
            "major": "Data Science",
            "starting_year": 2022,
            "total_attendance": 10,
            "standing": "B",
            "year": 2,
            "last_attendance_time": "2024-1-11 00:54:34"
        },
    "2223647":
        {
            "name": "Yashwant Sinha",
            "major": "Computer Science",
            "starting_year": 2020,
            "total_attendance": 10,
            "standing": "B",
            "year": 4,
            "last_attendance_time": "2024-1-11 00:54:34"
        },
    "2223829":
        {
            "name": "Angela Mascia",
            "major": "Physics",
            "starting_year": 2022,
            "total_attendance": 2,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2024-1-11 00:54:34"
        },
    "2236373":
        {
            "name": "Esther Macklin",
            "major": "English",
            "starting_year": 2019,
            "total_attendance": 7,
            "standing": "G",
            "year": 5,
            "last_attendance_time": "2024-12-11 00:54:34"
        }
}


for key, value in data.items():
    ref.child(key).set(value)


