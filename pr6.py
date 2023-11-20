import sqlite3
import json
import xml.etree.ElementTree as ET
from ftplib import FTP

class Student:
    def __init__(self, last_name, first_name, middle_name, group, birth_date=None, address=None):
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.group = group
        self.birth_date = birth_date
        self.address = address

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def set_birth_date(self, birth_date):
        self.birth_date = birth_date

    def set_address(self, address):
        self.address = address

    def to_dict(self):
        return {
            "last_name": self.last_name,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "group": self.group,
            "birth_date": self.birth_date,
            "address": self.address
        }

class Success:
    def __init__(self, subjects, scores):
        self.subjects = subjects
        self.scores = scores

    def average_score(self):
        return sum(self.scores) / len(self.scores)

class DesiredSuccess(Success):
    pass

class StudentData:
    def __init__(self, student, real_success, desired_success):
        self.student = student
        self.real_success = real_success
        self.desired_success = desired_success

class DataStorage:
    def save(self, data, filename):
        pass

class JSONDataStorage(DataStorage):
    def save(self, data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

class XMLDataStorage(DataStorage):
    def save(self, data, filename):
        root = ET.Element("data")
        student_elem = ET.SubElement(root, "student")
        student_elem.set("full_name", data.student.full_name)
        student_elem.set("group", data.student.group)

        for success_type in ["real_success", "desired_success"]:
            success_elem = ET.SubElement(student_elem, success_type)
            for subject, score in zip(getattr(data, success_type).subjects, getattr(data, success_type).scores):
                subject_elem = ET.SubElement(success_elem, "subject")
                subject_elem.set("name", subject)
                subject_elem.text = str(score)

        tree = ET.ElementTree(root)
        tree.write(filename)

class FTPUploader:
    def __init__(self, filename, ftp_connection):
        self.filename = filename
        self.ftp_connection = ftp_connection

    def upload(self):
        try:
            ftp = FTP(self.ftp_connection['host'])
            ftp.login(self.ftp_connection['user'], self.ftp_connection['password'])

            remote_directory = "/upload"
            ftp.cwd(remote_directory)

            with open(self.filename, 'rb') as file:
                ftp.storbinary(f'STOR {self.filename}', file)

            ftp.quit()
            print(f"File '{self.filename}' uploaded successfully to FTP server.")
        except Exception as e:
            print(f"Error uploading file to FTP server: {str(e)}")

class DatabaseSetup:
    def __init__(self, db_name):
        self.db_name = db_name

    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_data (
                id INTEGER PRIMARY KEY,
                student_json TEXT,
                real_success_json TEXT,
                desired_success_json TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print("Database table created successfully.")

def add_data_to_database(student_data_dict, real_success_dict, desired_success_dict):
    conn = sqlite3.connect("student_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_data (student_json, real_success_json, desired_success_json)
        VALUES (?, ?, ?)
    ''', (json.dumps(student_data_dict), json.dumps(real_success_dict), json.dumps(desired_success_dict)))
    conn.commit()
    conn.close()
    print("Data added to the database successfully.")

def query_database():
    conn = sqlite3.connect("student_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM student_data
    ''')
    rows = cursor.fetchall()
    conn.close()

    print("\nDatabase Content:")
    for row in rows:
        print(row)

if __name__ == "__main__":
    db_setup = DatabaseSetup("student_database.db")
    db_setup.create_table()

    student = Student("Doe", "John", "Smith", "CS101", "2000-01-01", "123 Main St")
    real_success = DesiredSuccess(["Math", "Physics", "Chemistry"], [90, 85, 92])
    desired_success = DesiredSuccess(["Math", "Physics", "Chemistry"], [95, 90, 95])
    student_data = StudentData(student, real_success, desired_success)

    student_data_dict = {
        "student": student.to_dict(),
        "real_success": {
            "subjects": real_success.subjects,
            "scores": real_success.scores
        },
        "desired_success": {
            "subjects": desired_success.subjects,
            "scores": desired_success.scores
        }
    }

    json_storage = JSONDataStorage()
    json_storage.save(student_data_dict, "student_data.json")

    xml_storage = XMLDataStorage()
    xml_storage.save(student_data, "student_data.xml")

    ftp_connection_info = {
        "host": "31.28.191.34",
        "user": "student@goodshop.com.ua",
        "password": "zu^DR{znaaYT"
    }
    uploader = FTPUploader("student_data.json", ftp_connection_info)
    uploader.upload()

    add_data_to_database(student_data_dict, real_success.__dict__, desired_success.__dict__)

    query_database()
