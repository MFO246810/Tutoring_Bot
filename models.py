import enum
import datetime
from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, BigInteger, Integer, Time, ForeignKey, DateTime, Text, Enum

class Base(DeclarativeBase):
    pass

class ROLES(enum.Enum):
    TUTOR = "Tutor"
    WORKSHOP_DIRECTOR = "Workshop_Director"
    
class DAYS_OF_THE_WEEK(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class DEED_STATUS(enum.Enum):
    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    UNCLAIMED = "Unclaimed"
    COMPLETED = "Completed"

class Active(enum.Enum):
    ACTIVE = "ACTIVE"
    NOTACTIVE = "NOTACTIVE"

class Tutor(Base):
    __tablename__ = "Tutor"

    Discord_ID: Mapped[str] = mapped_column(String(255), primary_key=True, nullable=False, unique=True)
    First_Name: Mapped[str] = mapped_column(String(255), nullable=False)
    Last_Name: Mapped[str] = mapped_column(String(255), nullable=False)
    Current_Role: Mapped[ROLES] = mapped_column(Enum(ROLES, name="roles", create_constraint=True), nullable=False)
    Is_Active: Mapped[Active] = mapped_column(Enum(Active, name="Active", create_constraint=True), nullable=False)

    # Relationships
    Availabilities: Mapped[List["Availability"]] = relationship(back_populates="tutor")
    Current_Courses: Mapped[List["Tutored_Courses"]] = relationship(back_populates="Course_Tutors")
    Current_points: Mapped["CurrentPoints"] = relationship(back_populates="Tutor_Points")

class CurrentPoints(Base):
    __tablename__ = "Current_Points"

    Discord_ID: Mapped[str] = mapped_column(String(255), ForeignKey("Tutor.Discord_ID"), primary_key=True, nullable=False)
    Deeds_Point: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    Tutor_Points: Mapped[Tutor] = relationship(back_populates="Current_points")

class Availability(Base):
    __tablename__ = "Availability"

    Availbility_ID: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    Discord_ID: Mapped[str] = mapped_column(
        String(255), ForeignKey("Tutor.Discord_ID"), nullable=False
    )
    Scheduled_Day: Mapped[DAYS_OF_THE_WEEK] = mapped_column(Enum(DAYS_OF_THE_WEEK, name="day_of_the_week", create_constraint=True), nullable=False)
    Start_Time: Mapped[Time] = mapped_column(Time, nullable=False)
    End_Time: Mapped[Time] = mapped_column(Time, nullable=False)

    # Relationships
    tutor: Mapped["Tutor"] = relationship(back_populates="Availabilities")

class Courses(Base):
    __tablename__ = "Courses"

    Courses_ID: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    Courses_Name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    #Relationships
    Actual_course: Mapped["Tutored_Courses"] = relationship(back_populates="course")

class Tutored_Courses(Base):
    __tablename__ = "Tutored_Courses"

    ID: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    Discord_ID: Mapped[str] = mapped_column(
        String(255), ForeignKey("Tutor.Discord_ID"), nullable=False
    )
    Courses_ID: Mapped[int] = mapped_column(BigInteger, ForeignKey("Courses.Courses_ID"), nullable=False)

    #Relationships
    Course_Tutors: Mapped[List[Tutor]]= relationship(back_populates="Current_Courses")
    course: Mapped["Courses"] = relationship(back_populates="Actual_course")

class Deeds(Base):
    __tablename__ = "Deeds"

    ID: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    Creator: Mapped[str] = mapped_column(String(255), nullable=False)
    Course_Name: Mapped[str] = mapped_column(String(30), nullable=False)
    Assigned_Tutor : Mapped[str] = mapped_column(String(255), ForeignKey("Tutor.Discord_ID"), nullable=True)
    Created_Time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    Original_Message: Mapped[str] = mapped_column(Text)
    Current_Status: Mapped[DEED_STATUS] = mapped_column(Enum(DEED_STATUS, name="deed_status", create_constraint=True), nullable=False)

class Announced_Deeds(Base):
    __tablename__ = "Announced_Deeds"

    Deed_ID: Mapped[int] = mapped_column(BigInteger, ForeignKey("Deeds.ID"), primary_key=True, nullable=False)

class Deeds_Logs(Base):
    __tablename__ = "Deeds_Logs"
    ID: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    Deed_ID: Mapped[int] = mapped_column(BigInteger, ForeignKey("Deeds.ID"), nullable=False)
    Log_Time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    Assigned_Tutor: Mapped[str] = mapped_column(String(255), ForeignKey("Tutor.Discord_ID"), nullable=False)
    Student : Mapped[str] = mapped_column(String(255), nullable=False)
    Topic_Covered : Mapped[str] = mapped_column(Text)

class Workshop_Deeds(Base):
    __tablename__ = "Workshop_Deeds"

    ID: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    Creator: Mapped[str] = mapped_column(String(255), nullable=False)
    Course_Name: Mapped[str] = mapped_column(String(30), nullable=False)
    Created_Time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    Current_Status: Mapped[DEED_STATUS] = mapped_column(Enum(DEED_STATUS, name="deed_status", create_constraint=True), nullable=False)
    Topic_Covered : Mapped[str] = mapped_column(Text)
    num_of_tutors: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

class Workshop_Deeds_Logs(Base):
    __tablename__ = "Workshop_Deeds_Logs"

    ID: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    Workshop_Deed_ID: Mapped[int] = mapped_column(BigInteger, ForeignKey("Workshop_Deeds.ID"), nullable=False)
    Log_Time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    Tutor: Mapped[str] = mapped_column(String(255), ForeignKey("Tutor.Discord_ID"), nullable=False)

class Workshop_Participations(Base):
    __tablename__ = "Workshop_Participation"

    Workshop_Deed_ID: Mapped[int] = mapped_column(BigInteger, ForeignKey("Workshop_Deeds.ID"), primary_key=True, nullable=False)
    Tutor: Mapped[str] = mapped_column(String(255), ForeignKey("Tutor.Discord_ID"), nullable=False)
