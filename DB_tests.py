import os
import discord
from models import Base
from datetime import datetime, time, date
from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import View, Button
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import Tutor, CurrentPoints, Availability, DAYS_OF_THE_WEEK, DEED_STATUS, Deeds

load_dotenv()
engine = create_engine(os.getenv("Database_uri"), echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
Current_time = time(15,30,00)
Day_of_the_week = 3

stmt = select(Deeds)
result = session.execute(stmt).scalars().all()
print(result)
for res in result:
    print("Deed ID: ", res.ID, "Tutor: ", res.Assigned_Tutor, "Current Status: ", res.Current_Status)