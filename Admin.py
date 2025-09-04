import os
import time as t
import logging
import discord
from models import Base
from dotenv import load_dotenv
from discord.ui import View, Button
from discord.ext import tasks, commands
from sqlalchemy.orm import sessionmaker
from datetime import datetime, time, date
from sqlalchemy import create_engine, select, func
from setup import Add_Availabilities, Add_Tutors, Add_TUTORED_COURSES
from models import Tutor, CurrentPoints, DEED_STATUS, ROLES, Active, Workshop_Deeds, Workshop_Participations, Workshop_Deeds_Logs

logging.basicConfig(
    level=logging.INFO,  # DEBUG / INFO / WARNING / ERROR / CRITICAL
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("Deed_Manager.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
discord.utils.setup_logging(level=logging.INFO, root=False)
bot_logger = logging.getLogger("Tutoring_Bot")
commands_logger = logging.getLogger("Tutoring_Bot.commands")

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
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
        bot_logger.info(f"New tutor form submitted by {interaction.user.name}")
        Discord_ID = self.Discord_ID.value
        First_Name = self.First_Name.value
        Last_Name = self.Last_Name.value
        if self.Role.value == "1":
            Role = ROLES.TUTOR
        elif self.Role.value == "2":
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
        bot_logger.info(f"New tutor {Discord_ID} added successfully")
        await interaction.response.send_message(f"This tutor: {Discord_ID} has been sucessfully added", ephemeral=True)

class Del_tutor(discord.ui.Modal, title="Delete Tutor form"):
    Discord_ID = discord.ui.TextInput(label="Discord Username", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        bot_logger.info(f"Delete tutor form submitted by {interaction.user.name}")
        Discord_ID = self.Discord_ID.value
        v_stmt = select(Tutor).where(Tutor.Discord_ID == Discord_ID)
        Current_Tutor = session.execute(v_stmt).scalars().first()
        if(Current_Tutor):
            Current_Tutor.Is_Active = Active.NOTACTIVE
            session.commit()
            bot_logger.info(f"Tutor {Discord_ID} deleted successfully")
            await interaction.response.send_message(f"This tutor: {Discord_ID} has been sucessfully deleted", ephemeral=True)
        else:
            bot_logger.warning(f"Tutor {Discord_ID} not found for deletion")
            await interaction.response.send_message(f"This person: {Discord_ID} is not a tutor", ephemeral=True)

class Alter_Tutor_points(discord.ui.Modal, title="Alter Point Value"):
    Discord_ID = discord.ui.TextInput(label="Discord Username", style=discord.TextStyle.short)
    New_Point_Value = discord.ui.TextInput(label="New Points Value", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        bot_logger.info(f"Alter points form submitted by {interaction.user.name}")
        Discord_ID = self.Discord_ID.value
        New_Point_Value = int(self.New_Point_Value.value)

        v_stmt = select(Tutor).where(Tutor.Discord_ID == Discord_ID)
        Current_Tutor = session.execute(v_stmt).scalars().first()
        if(Current_Tutor and Current_Tutor.Is_Active == Active.ACTIVE):
            bot_logger.info(f"Altering points for tutor {Discord_ID} to {New_Point_Value}")
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
            bot_logger.info(f"Tutor {Discord_ID} points changed successfully from {former_value} to {New_Point_Value}")
            await interaction.response.send_message(f"This tutor: {Discord_ID} points has been changed sucessfully from {former_value} to {New_Point_Value}", ephemeral=True)

class Workshop_Course_List(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(
        placeholder="Please select the course you are making the workshop for: ",
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
        bot_logger.info(f"Workshop course selected by {interaction.user.name}")
        await interaction.message.delete()
        workshop_course = select.values[0]
        username = interaction.user.name
        await interaction.response.send_modal(Create_Workshop_deeds(self.bot, workshop_course, username))

class Create_Workshop_deeds(discord.ui.Modal, title="Create Workshop Deeds"):
    def __init__(self, bot, courses, username):
        super().__init__(timeout=None)
        self.bot = bot
        self.course = courses
        self.username = username
    
    num_of_tutors = discord.ui.TextInput(label="Number of Tutors Needed", style=discord.TextStyle.short)
    Topics_Covered = discord.ui.TextInput(label="Topics to be covered", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        num_of_tutors = self.num_of_tutors.value
        Topics_Covered = self.Topics_Covered.value
        print(type(Topics_Covered)) 
        print(Workshop_Deeds.__table__)     
        Deed_ID = current_milli_time()
        New_Workshop_deeds =  Workshop_Deeds(
            ID=Deed_ID,
            Creator=self.username,
            Course_Name=self.course,
            Created_Time = datetime.now(),
            Current_Status = DEED_STATUS.UNCLAIMED,
            num_of_tutors = num_of_tutors,
            Topic_Covered = Topics_Covered
        )
        session.add(New_Workshop_deeds)
        bot_logger.info(f"Workshop deed creation submitted by {interaction.user.name} for course {self.course}")
        session.commit()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
        embed = discord.Embed(
            title="Workshop Deed",
            description=f"New Workshop Course has been annouced ",
            color=discord.Color.red()  
        ) 
        embed.add_field(name=f"Deed ID: ", value=f"{Deed_ID}", inline=True)
        embed.add_field(name=f"Needed Tutors", value=f"{num_of_tutors}", inline=True)
        embed.add_field(name="Current number of tutors: ", value=f"0", inline=True)
        embed.add_field(name=f"Topic to be covered", value=f"{Topics_Covered}", inline=True)
        self.update_channel_id = int(os.getenv("Discord_Workshop_Channel"))
        self.update_channel = await self.bot.fetch_channel(self.update_channel_id)
        view = Claim_Workshop_deed(Deed_ID)
        await self.update_channel.send(embed=embed, view=view)
        bot_logger.info(f"Workshop deed {Deed_ID} created successfully for course {self.course}")
        await interaction.response.send_message(f"The workshop deed has been created an it is currently in the open workshop channel", ephemeral=True)

class Claim_Workshop_deed(discord.ui.View):
    def __init__(self, deed_ID):
        super().__init__(timeout=None)
        self.deed_id = deed_ID

    @discord.ui.button(label="Join the team", style=discord.ButtonStyle.green)
    async def button_callback (self, interaction: discord.Interaction, button: discord.ui.Button):
        bot_logger.info(f"Join team button clicked by {interaction.user.name} for deed {self.deed_id}")
        stmt = select(Workshop_Deeds).where(Workshop_Deeds.ID == self.deed_id, Workshop_Deeds.Current_Status == DEED_STATUS.COMPLETED)
        status = session.execute(stmt).scalars().all()
        if(status):
            bot_logger.info(f"Deed {self.deed_id} is already closed, cannot join team - {interaction.user.name} attempted to join")
            await interaction.response.send_message(f"This deed is already closed", ephemeral=True)
            return
        tutor = interaction.user.name
        stmt = select(Tutor).where(Tutor.Discord_ID == tutor)
        Current_Tutor = session.execute(stmt).scalars().first()
        if(Current_Tutor):
            stmt = select(Workshop_Participations).where(Workshop_Participations.Workshop_Deed_ID == self.deed_id, 
                                                         Workshop_Participations.Tutor == Current_Tutor.Discord_ID)
            Tutor_Confirm = session.execute(stmt).scalars().all()
            if(Tutor_Confirm):
                bot_logger.info(f"Tutor {Current_Tutor.Discord_ID} has already registered for deed {self.deed_id}, cannot join again")
                await interaction.response.send_message(f"You have already registered for this deed", ephemeral=True)
                return
            stmt = select(Workshop_Participations).where(Workshop_Participations.Workshop_Deed_ID == self.deed_id)
            Participant_List = session.execute(stmt).scalars().all()
            stmt = select(Workshop_Deeds).where(Workshop_Deeds.ID == self.deed_id)
            Workshop = session.execute(stmt).scalars().first()
            Num_of_tutors = Workshop.num_of_tutors
            if(len(Participant_List) >= int(Num_of_tutors)):
                await interaction.response.send_message(f"The amount of tutor has already been reached", ephemeral=True)
                bot_logger.info(f"Deed {self.deed_id} has reached max tutors, cannot join - {interaction.user.name} attempted to join")
                return
            else: 
                await interaction.message.delete()
                workshop_part = Workshop_Participations(
                    Workshop_Deed_ID = self.deed_id,
                    Tutor=tutor
                )
                session.add(workshop_part)
                bot_logger.info(f"Tutor {tutor} added to deed {self.deed_id} participation list")
                session.commit
                embed = discord.Embed(
                title="Workshop Deed",
                description=f"New Workshop Course has been annouced ",
                color=discord.Color.red()  
                ) 
                embed.add_field(name=f"Deed ID: ", value=f"{Workshop.ID}", inline=True)
                embed.add_field(name=f"Needed Tutors", value=f"{Num_of_tutors}", inline=True)
                embed.add_field(name="Current number of tutors: ", value=f"{len(Participant_List) + 1}", inline=True)
                embed.add_field(name=f"Topic to be covered", value=f"{Workshop.Topic_Covered}", inline=True)
                await interaction.user.send(f"You have been added to the deed team expect to be contacted by Franklin on the details of the workshop")
                await interaction.response.send_message(embed=embed, view=Claim_Workshop_deed(Workshop.ID))

class Complete_Workshop_Deeds(discord.ui.Modal, title="Complete Workshop Deed"):
    Deed_ID = discord.ui.TextInput(label="Deed ID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        bot_logger.info(f"Complete workshop deed form submitted by {interaction.user.name} for deed {self.Deed_ID.value}")      
        student = interaction.user.name
        Deed_id = int(self.Deed_ID.value)
        v_stmt = select(Tutor).where(Tutor.Discord_ID == student)
        Current_Tutor = session.execute(v_stmt).scalars().first()
        if(Current_Tutor):
            stmt = select(Workshop_Deeds).where(Workshop_Deeds.ID == Deed_id)
            Current_Deed = session.execute(stmt).scalars().first()
            Workshop_log = Workshop_Deeds_Logs(
                ID=current_milli_time(),
                Workshop_Deed_ID=Current_Deed.ID,
                Log_Time=datetime.now(),
                Tutor=Current_Tutor.Discord_ID
            )
            session.add(Workshop_log)
            stmt = select(CurrentPoints).where(CurrentPoints.Discord_ID == Current_Tutor.Discord_ID)
            Current_Points = session.execute(stmt).scalars().first()
            bot_logger.info(f"Workshop deed {Deed_id} completed by tutor {Current_Tutor.Discord_ID}")
            if(Current_Points):
                Current_Points.Deeds_Point = Current_Points.Deeds_Point + 2
                point_Embed =discord.Embed(
                    title="Deed Recorded Sucessfully",
                    description=f"Run /Leaderboard to see current rankings as well as /Current_Points to be dmed your point value",
                    color=discord.Color.green()  
                )
                await interaction.response.send_message(embed=point_Embed)
            else:
                New_Point_Haver = CurrentPoints(
                    Discord_ID = Current_Tutor.Discord_ID,
                    Deeds_Point = 1
                )
                point_Embed =discord.Embed(
                    title="Deed Recorded Sucessfully",
                    description=f"Run /Leaderboard to see current rankings as well as /Current_Points to be dmed your point value",
                    color=discord.Color.green()  
                )
                await interaction.response.send_message(embed=point_Embed)
                session.add(New_Point_Haver)
                session.commit()
            Current_Deed.Current_Status = DEED_STATUS.COMPLETED
            session.commit()
            bot_logger.info(f"Workshop deed {Deed_id} status updated to COMPLETED")
        else:
            bot_logger.warning(f"User {student} is not a tutor, cannot complete deed {Deed_id}")
            await interaction.response.send_message(f"You are not a tutor you cannot run this command", ephemeral=True)

class View_All_Tutors():
    async def View_Embed():
        bot_logger.info("Generating current tutors embed")
        stmt = select(Tutor).join(Tutor.Current_points)
        All_Tutors = session.execute(stmt).scalars().all()
        tutors_embed = discord.Embed(
            title="Current Tutors",
            description=f"Here is a list of current tutors",
            color=discord.Color.blue() 
        )
        for tutor in All_Tutors:
            tutors_embed.add_field(name=f"{tutor.First_Name} {tutor.Last_Name}: ", value=f"{tutor.Current_points.Deeds_Point}", inline=True)
        return tutors_embed
    
class Add_From_Files(discord.ui.View):
    def __init__(self, filepath):
        super().__init__(timeout=None)
        self.filepath = filepath

    @discord.ui.select(
        placeholder="Select the type of data: ",
        options=[
            discord.SelectOption(label="Tutor", value="1"),
            discord.SelectOption(label="Availabilities", value="2"),
            discord.SelectOption(label="Tutored Courses", value="3")
        ]
    )

    async def on_submit(self, interaction: discord.Interaction, select):
        option = select.values[0]
        if option  == "1" :
            bot_logger.info(f"Adding tutors from file {self.filepath} as requested by {interaction.user.name}")
            Add_Tutors(self.filepath)
        elif option == "2":
            bot_logger.info(f"Adding availabilities from file {self.filepath} as requested by {interaction.user.name}")
            Add_Availabilities(self.filepath)
        elif option == "3":
            bot_logger.info(f"Adding tutored courses from file {self.filepath} as requested by {interaction.user.name}")
            Add_TUTORED_COURSES(self.filepath)
        await interaction.response.send_message(f"Data has been added successfully", ephemeral=True)
        await interaction.message.delete() 




