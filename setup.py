import os
import csv
import time
from datetime import datetime
from models import Base
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from models import Courses, Tutor, ROLES, Availability, DAYS_OF_THE_WEEK, Tutored_Courses

load_dotenv()
engine = create_engine(os.getenv("Database_uri"), echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

AVAILABILITIES = "Tutoring_Bot_availabilities.csv"
CURRENT_TUTORS = "Tutoring_Bot_Current_Tutors.csv"
TUTORED_COURSES = "Tutoring_Bot_Tutored_Couses.csv"

def current_milli_time():
    return round(time.time() * 1000)

def Add_courses():
    COURSE_LIST = ["COSC-1336", "COSC-1436", "COSC-2436", "COSC-2425", "COSC-3320", "COSC-3340", "COSC-3360", "COSC-3380"]
    for course in COURSE_LIST:
        New_course = Courses(Courses_ID=current_milli_time(), Courses_Name=course)
        session.add(New_course)
        session.commit()

def Add_Tutors():
    with open(CURRENT_TUTORS, 'r') as file:
        CSV_FILE = csv.DictReader(file)
        for row in CSV_FILE:
            row['Role'] = int(row['Role'])
            if(row['Role'] == 0):
                New_Tutor = Tutor(Discord_ID=row['Discord_ID'], First_Name=row['First_Name'], Last_Name=row['Last_Name'], Current_Role=ROLES.TUTOR)
                session.add(New_Tutor)
                session.commit()
            elif(row['Role'] == 1):
                New_Tutor = Tutor(Discord_ID=row['Discord_ID'], First_Name=row['First_Name'], Last_Name=row['Last_Name'], Current_Role=ROLES.WORKSHOP_DIRECTOR)
                session.add(New_Tutor)
                session.commit()

def Add_Availabilities():
    with open(AVAILABILITIES, 'r') as file:
        CSV_FILE = csv.DictReader(file)
        for row in CSV_FILE:
            print(row)
            Start_time = datetime.strptime(row['Start_Time'], "%H:%M:%S").time()
            End_time = datetime.strptime(row['End_TIme'], "%H:%M:%S").time()
            row['Scheduled_Day']  = int(row['Scheduled_Day'] )
            if(row['Scheduled_Day'] == 1):
                New_Availability = Availability(
                    Availbility_ID=current_milli_time(), 
                    Discord_ID=row["Discord_ID"], 
                    Scheduled_Day=DAYS_OF_THE_WEEK.MONDAY, 
                    Start_Time=Start_time, 
                    End_Time=End_time)
                session.add(New_Availability)
                session.commit()
            elif(row['Scheduled_Day'] == 2):
                New_Availability = Availability(
                    Availbility_ID=current_milli_time(), 
                    Discord_ID=row["Discord_ID"], 
                    Scheduled_Day=DAYS_OF_THE_WEEK.TUESDAY, 
                    Start_Time=Start_time, 
                    End_Time=End_time)
                session.add(New_Availability)
                session.commit()
            elif(row['Scheduled_Day'] == 3):
                New_Availability = Availability(
                    Availbility_ID=current_milli_time(), 
                    Discord_ID=row["Discord_ID"], 
                    Scheduled_Day=DAYS_OF_THE_WEEK.WEDNESDAY, 
                    Start_Time=Start_time, 
                    End_Time=End_time)
                session.add(New_Availability)
                session.commit()
            elif(row['Scheduled_Day'] == 4):
                New_Availability = Availability(
                    Availbility_ID=current_milli_time(), 
                    Discord_ID=row["Discord_ID"], 
                    Scheduled_Day=DAYS_OF_THE_WEEK.THURSDAY, 
                    Start_Time=Start_time, 
                    End_Time=End_time)
                session.add(New_Availability)
                session.commit()
            elif(row['Scheduled_Day'] == 5):
                New_Availability = Availability(
                    Availbility_ID=current_milli_time(), 
                    Discord_ID=row["Discord_ID"], 
                    Scheduled_Day=DAYS_OF_THE_WEEK.FRIDAY, 
                    Start_Time=Start_time, 
                    End_Time=End_time)
                session.add(New_Availability)
                session.commit()
            elif(row['Scheduled_Day'] == 6):
                New_Availability = Availability(
                    Availbility_ID=current_milli_time(), 
                    Discord_ID=row["Discord_ID"], 
                    Scheduled_Day=DAYS_OF_THE_WEEK.SATURDAY, 
                    Start_Time=Start_time, 
                    End_Time=End_time)
                session.add(New_Availability)
                session.commit()
            elif(row['Scheduled_Day'] == 7):
                New_Availability = Availability(
                    Availbility_ID=current_milli_time(), 
                    Discord_ID=row["Discord_ID"], 
                    Scheduled_Day=DAYS_OF_THE_WEEK.SUNDAY, 
                    Start_Time=Start_time, 
                    End_Time=End_time)
                session.add(New_Availability)
                session.commit()

def Add_TUTORED_COURSES():
    with open(TUTORED_COURSES, 'r') as file:
        CSV_FILE = csv.DictReader(file)
        for row in CSV_FILE:
            stmt = select(Courses.Courses_ID).where(Courses.Courses_Name == row['Courses_ID'])
            Courses_ID = session.execute(stmt).scalars().all()
            print("Courses: ", Courses_ID)
            New_Tutored_Courses = Tutored_Courses(ID=row['ID'], Discord_ID=row["Discord_ID"], Courses_ID=Courses_ID[0])
            session.add(New_Tutored_Courses)
            session.commit()

Add_courses()          
Add_Tutors()
Add_Availabilities()
Add_TUTORED_COURSES()