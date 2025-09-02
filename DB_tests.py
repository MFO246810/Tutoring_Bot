import os
import discord
from models import Base
from datetime import datetime, time, date
from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import View, Button
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import Tutor, CurrentPoints, Availability, DAYS_OF_THE_WEEK, DEED_STATUS, Deeds, Workshop_Deeds

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

print(Workshop_Deeds.__table__)  