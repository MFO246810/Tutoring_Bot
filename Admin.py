import os
import time as t
import discord
from models import Base
from dotenv import load_dotenv
from discord.ui import View, Button
from discord.ext import tasks, commands
from sqlalchemy.orm import sessionmaker
from datetime import datetime, time, date
from sqlalchemy import create_engine, select, func
from models import Tutor, CurrentPoints, Availability, DAYS_OF_THE_WEEK, DEED_STATUS, Deeds, Announced_Deeds, Deeds_Logs, Tutored_Courses, Courses, ROLES, Active, Workshop_Deeds

load_dotenv()
engine = create_engine(os.getenv("Database_uri"), echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def current_milli_time():
    return round(t.time() * 1000)


class add_new_tutor(discord.ui.Modal, title="New Tutor form"):
    Discord_ID = discord.ui.TextInput(label="Discord Username", style=discord.TextStyle.short)
    First_Name = discord.ui.TextInput(label="First Name", style=discord.TextStyle.short)
    Last_Name = discord.ui.TextInput(label="Last Name", style=discord.TextStyle.short)
    Role = discord.ui.TextInput(label="Role 1 for Tutor | 2 for Workshop director", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        Discord_ID = self.Discord_ID.value
        First_Name = self.First_Name.value
        Last_Name = self.Last_Name.value
        if self.Role.value == 1:
            Role = ROLES.TUTOR
        elif self.Role.value == 2:
            Role = ROLES.WORKSHOP_DIRECTOR
        
        New_Tutor = Tutor(
            Discord_ID=Discord_ID,
            First_Name=First_Name,
            Last_Name=Last_Name,
            Current_Role=Role,
            Is_Active=Active.ACTIVE
        )
        session.add(New_Tutor)
        session.commit()
        interaction.response.send_message(f"This tutor: {Discord_ID} has been sucessfully added", ephermal=True)

class Del_tutor(discord.ui.Modal, title="Delete Tutor form"):
    Discord_ID = discord.ui.TextInput(label="Discord Username", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        Discord_ID = self.Discord_ID.value
        v_stmt = select(Tutor).where(Tutor.Discord_ID == Discord_ID)
        Current_Tutor = session.execute(v_stmt).scalars().first()
        if(Current_Tutor):
            Current_Tutor.Is_Active = Active.NOTACTIVE
            session.commit()
            interaction.response.send_message(f"This tutor: {Discord_ID} has been sucessfully deleted", ephermal=True)
        else:
            interaction.response.send_message(f"This person: {Discord_ID} is not a tutor", ephermal=True)

class Alter_Tutor_points(discord.ui.Modal, title="Alter Point Value"):
    Discord_ID = discord.ui.TextInput(label="Discord Username", style=discord.TextStyle.short)
    New_Point_Value = discord.ui.TextInput(label="New Points Value", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        Discord_ID = self.Discord_ID.value
        New_Point_Value = int(self.New_Point_Value.value)

        v_stmt = select(Tutor).where(Tutor.Discord_ID == Discord_ID)
        Current_Tutor = session.execute(v_stmt).scalars().first()
        if(Current_Tutor and Current_Tutor.Is_Active == Active.ACTIVE):
            if(Current_Tutor.Current_points == None):
                New_Point_Haver = CurrentPoints(
                    Discord_ID = Current_Tutor.Discord_ID,
                    Deeds_Point = New_Point_Value
                )
                session.add(New_Point_Haver)
                former_value = 0
            else:
                former_value = Current_Tutor.Current_points
                Current_Tutor.Current_points = New_Point_Value
            session.commit()
            interaction.response.send_message(f"This tutor: {Discord_ID} points has been changed sucessfully from {former_value} to {New_Point_Value}", ephermal=True)

class Workshop_Course_List(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(
        placeholder="Please select the course you need help with: ",
        options=[
            discord.SelectOption(label="COSC-1336", value="COSC-1336"),
            discord.SelectOption(label="COSC-1436", value="COSC-1436"),
            discord.SelectOption(label="COSC-2436", value="COSC-2436"),
            discord.SelectOption(label="COSC-2425", value="COSC-2425"),
            discord.SelectOption(label="COSC-3320", value="COSC-3320"),
            discord.SelectOption(label="COSC-3340", value="COSC-3340"),
            discord.SelectOption(label="COSC-3360", value="COSC-3360"),
            discord.SelectOption(label="COSC-3380", value="COSC-3380")
        ]
    )
    async def Chosen_Courses(self, interaction: discord.Interaction, select):
        workshop_course = select.values[0]
        username = interaction.user.name
        await interaction.response.send_modal(Create_Workshop_deeds(self.bot, workshop_course, username))

class Create_Workshop_deeds(discord.ui.Modal, title="Create Workshop Deeds"):
    def __init__(self, courses, username):
        super().__init__(timeout=None)
        self.course = courses
        self.username = username
    
    num_of_tutors = discord.ui.TextInput(label="Number of Tutors Needed", style=discord.TextStyle.short)
    Topics_Covered = discord.ui.TextInput(label="Topics to be covered", style=discord.TextStyle.paragraph)

    async def Chosen_Courses(self, interaction: discord.Interaction, select):
        workshop_course = select.values[0]
        username = interaction.user.name
        num_of_tutors = self.num_of_tutors.value
        Topics_Covered = self.Topics_Covered.value       

        New_Workshop_deeds =  Workshop_Deeds(
            ID=current_milli_time(),
            Creator=username,
            Course_Name=workshop_course,
            Created_Time = datetime.now(),
            Current_Status = DEED_STATUS.UNCLAIMED,
            num_of_tutors = num_of_tutors,
            Topics_Covered = Topics_Covered
        )
        embed = discord.Embed(
            title="Workshop Deed",
            description=f"New Workshop Course has been annouced ",
            color=discord.Color.red()  
        ) 
        embed.add_field(name=f"Needed Tutors", value=f"{num_of_tutors}", inline=True)
        embed.add_field(name=f"Topic to be covered", value=f"{Topics_Covered}", inline=True)
        session.add(New_Workshop_deeds)
        session.commit()



    
    
        


