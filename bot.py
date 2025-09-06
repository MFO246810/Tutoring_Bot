import os
import time as t
import discord
import logging
from info import info
from models import Base
from dotenv import load_dotenv
from discord import app_commands
from discord.ui import View, Button
from discord.ext import tasks, commands
from sqlalchemy.orm import sessionmaker
from datetime import datetime, time, date
from sqlalchemy import create_engine, select, func
from models import Tutor, CurrentPoints, Availability, DAYS_OF_THE_WEEK, DEED_STATUS, Deeds, Announced_Deeds, Deeds_Logs, Tutored_Courses, Courses
from Admin import add_new_tutor, Del_tutor, Alter_Tutor_points, Workshop_Course_List, View_All_Tutors, Complete_Workshop_Deeds, Add_From_Files

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
Diretor_Discord = "iliketosleep2468"

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

def current_milli_time():
    return round(t.time() * 1000)

def get_user(Current_time, Day_of_the_week, courses):
    bot_logger.info(f"Fetching available tutors for course {courses} at time {Current_time} on day {Day_of_the_week}")
    if(Day_of_the_week == 1):
        stmt = select(Availability.Discord_ID).join(Availability.tutor).join(Tutor.Current_Courses).join(Tutored_Courses.course).where(
        Availability.Start_Time <= Current_time,
        Availability.End_Time >= Current_time,
        Availability.Scheduled_Day == DAYS_OF_THE_WEEK.MONDAY,
        Courses.Courses_Name == courses
    )
    elif(Day_of_the_week == 2):
        stmt = select(Availability.Discord_ID).join(Availability.tutor).join(Tutor.Current_Courses).join(Tutored_Courses.course).where(
        Availability.Start_Time <= Current_time,
        Availability.End_Time >= Current_time,
        Availability.Scheduled_Day == DAYS_OF_THE_WEEK.TUESDAY,
        Courses.Courses_Name == courses
    )
    elif(Day_of_the_week == 3):
        stmt = select(Availability.Discord_ID).join(Availability.tutor).join(Tutor.Current_Courses).join(Tutored_Courses.course).where(
        Availability.Start_Time <= Current_time,
        Availability.End_Time >= Current_time,
        Availability.Scheduled_Day == DAYS_OF_THE_WEEK.WEDNESDAY,
        Courses.Courses_Name == courses
    )
    elif(Day_of_the_week == 4):
        stmt = select(Availability.Discord_ID).join(Availability.tutor).join(Tutor.Current_Courses).join(Tutored_Courses.course).where(
        Availability.Start_Time <= Current_time,
        Availability.End_Time >= Current_time,
        Availability.Scheduled_Day == DAYS_OF_THE_WEEK.THURSDAY,
        Courses.Courses_Name == courses
    )
    elif(Day_of_the_week == 5):
        stmt = select(Availability.Discord_ID).join(Availability.tutor).join(Tutor.Current_Courses).join(Tutored_Courses.course).where(
        Availability.Start_Time <= Current_time,
        Availability.End_Time >= Current_time,
        Availability.Scheduled_Day == DAYS_OF_THE_WEEK.FRIDAY,
        Courses.Courses_Name == courses
    )
    elif(Day_of_the_week == 6):
        stmt = select(Availability.Discord_ID).join(Availability.tutor).join(Tutor.Current_Courses).join(Tutored_Courses.course).where(
        Availability.Start_Time <= Current_time,
        Availability.End_Time >= Current_time,
        Availability.Scheduled_Day == DAYS_OF_THE_WEEK.SATURDAY,
        Courses.Courses_Name == courses
    )
    elif(Day_of_the_week == 7):
        stmt = select(Availability.Discord_ID).join(Availability.tutor).join(Tutor.Current_Courses).join(Tutored_Courses.course).where(
        Availability.Start_Time <= Current_time,
        Availability.End_Time >= Current_time,
        Availability.Scheduled_Day == DAYS_OF_THE_WEEK.SUNDAY,
        Courses.Courses_Name == courses
    )
    else:
        return None

    result = session.execute(stmt).scalars().all()
    return result

class __Question_Forms__(discord.ui.Modal, title="Question Form"):
    def __init__(self, courses, bot):
        super().__init__(timeout=None)
        self.course = courses
        self.bot = bot
    Question = discord.ui.TextInput(label="Please enter question", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        bot_logger.info(f"Question form submitted by {interaction.user.name} for course {self.course}")
        message = self.Question.value
        guild =interaction.guild
        student = interaction.user.name
        Deed_ID = current_milli_time()
        New_Deeds = Deeds(
            ID = Deed_ID,
            Creator=student,
            Course_Name=self.course,
            Created_Time=datetime.now(),
            Original_Message=message,
            Current_Status = DEED_STATUS.UNCLAIMED
        )
        session.add(New_Deeds)
        session.commit()
        self.view = _Buttons_(Deed_ID)
        embed = discord.Embed(
            title="New Deed",
            description=f"{student} requires help with {self.course}",
            color=discord.Color.red()  
        ) 
        embed.add_field(name="Original Message", value=f"{message}", inline=False)
        embed.add_field(name="Deed ID: ", value=f"{Deed_ID}", inline=False)
        embed.set_author(name="Deed Informer")
        now = datetime.now()
        #print("Current Time: ", now.strftime("%H:%M:%S"))
        print("Current Time Object: ", now.time())
        Current_time = now.time()
        Day_of_the_week = now.weekday()
        tutors = get_user(Current_time=Current_time, Day_of_the_week=Day_of_the_week, courses=self.course)
        print("Tutors: ", tutors)
        if(len(tutors) == 0):
            bot_logger.warning(f"No tutors available for course {self.course} at time {Current_time} on day {Day_of_the_week}")
            await interaction.response.send_message(f"A tutor has been made aware of your question and will be reaching out. Course name: {self.course}", ephemeral=True)
            self.update_channel_id = int(os.getenv("Discord_Channel_ID"))
            self.update_channel = await self.bot.fetch_channel(self.update_channel_id)
            Update_Emded = discord.Embed(
                title="Unclaimed Deed",
                description=f"{student} requires help with {self.course} ",
                color=discord.Color.red() 
            )
            Update_Emded.add_field(name="Original Message", value=f"{message}", inline=False)
            Update_Emded.add_field(name="Deed ID: ", value=f"{Deed_ID}", inline=False)
            Update_Emded.set_author(name="Deed Informer")
            view = _Buttons_(Deed_ID)
            if self.update_channel:
                await self.update_channel.send(embed=Update_Emded, view=view)
                Deed_Announcement = Announced_Deeds(Deed_ID=Deed_ID)
                session.add(Deed_Announcement)
                session.commit()
                bot_logger.info(f"All tutors have been made aware of the students question in channel {self.update_channel_id}")
                return
            else:
                bot_logger.info(f"{self.update_channel} is not available")
                print("Channel Not avaliable", self.update_channel)
                return
        for tutor_name in tutors:
            target_user = discord.utils.get(guild.members, name=tutor_name)
            print("Target User: ", target_user)
            if target_user:
                try:
                    await target_user.send(embed=embed, view=self.view)
                    bot_logger.info(f"Sent DM to tutor {tutor_name} for deed {Deed_ID}")
                    await interaction.response.send_message(f"A tutor has been made aware of your question and will be reaching out. Course name: {self.course}", ephemeral=True)
                except discord.Forbidden:
                    bot_logger.error(f"Could not send DM to tutor {tutor_name} for deed {Deed_ID}")
                    await interaction.response.send_message(f"Could not send DM to {target_user.name}. They may have DMs disabled or blocked the bot.")
            else:
                bot_logger.warning(f"User {tutor_name} could not be found in guild {guild.name}")
                await Diretor_Discord.send(f"User {tutor_name} could not be found in guild {guild.name} please reach out to them and look at the logs with /logs in admin panel")
                await interaction.response.send_message("User could not be found")
        
class Course_List(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(
        placeholder="Please select the course you need help with: ",
        options=[
            discord.SelectOption(label="COSC-1336", value="COSC-1336"),
            discord.SelectOption(label="COSC-1437", value="COSC-1437"),
            discord.SelectOption(label="COSC-2436", value="COSC-2436"),
            discord.SelectOption(label="COSC-2425", value="COSC-2425"),
            discord.SelectOption(label="COSC-3320", value="COSC-3320"),
            discord.SelectOption(label="COSC-3340", value="COSC-3340"),
            discord.SelectOption(label="COSC-3360", value="COSC-3360"),
            discord.SelectOption(label="COSC-3380", value="COSC-3380")
        ]
    )
    async def Chosen_Courses(self, interaction: discord.Interaction, select):
        await interaction.message.delete()
        bot_logger.info(f"Course {select.values[0]} selected by {interaction.user.name}")
        print("Select: ", select.values[0])
        await interaction.response.send_modal(__Question_Forms__(select.values[0], self.bot))

class Deeds_List(discord.ui.View):
    @discord.ui.select(
        placeholder="Please select the type of deed: ",
        options=[
            discord.SelectOption(label="Online", value="1"),
            discord.SelectOption(label="In-Person", value="2"),
            discord.SelectOption(label="Workshop", value="3")
        ]
    )

    async def on_submit(self, interaction: discord.Interaction, select):
        await interaction.message.delete()
        bot_logger.info(f"Deed type {select.values[0]} selected by {interaction.user.name}")
        print("Select: ", select.values[0])
        if(select.values[0] == "1"):
            bot_logger.info(f"Sending complete deeds modal to {interaction.user.name}")
            await interaction.response.send_modal(Complete_Deeds())
        elif(select.values[0] == "2"):
            bot_logger.info(f"Sending complete in-person deeds course list to {interaction.user.name}")
            await interaction.response.send_message(view=Complete_Deeds_Course_List())
        elif(select.values[0] == "3"):
            bot_logger.info(f"Sending complete workshop deeds modal to {interaction.user.name}")
            await interaction.response.send_modal(Complete_Workshop_Deeds())

class Complete_Deeds_Course_List(discord.ui.View):
    @discord.ui.select(
        placeholder="Please select the course you turtored: ",
        options=[
            discord.SelectOption(label="COSC-1336", value="COSC-1336"),
            discord.SelectOption(label="COSC-1437", value="COSC-1437"),
            discord.SelectOption(label="COSC-2436", value="COSC-2436"),
            discord.SelectOption(label="COSC-2425", value="COSC-2425"),
            discord.SelectOption(label="COSC-3320", value="COSC-3320"),
            discord.SelectOption(label="COSC-3340", value="COSC-3340"),
            discord.SelectOption(label="COSC-3360", value="COSC-3360"),
            discord.SelectOption(label="COSC-3380", value="COSC-3380")
        ]
    )

    async def on_submit(self, interaction: discord.Interaction, select):
        bot_logger.info(f"Deeds course {select.values[0]} selected by {interaction.user.name}")
        await interaction.message.delete()
        print("Select: ", select.values[0])
        await interaction.response.send_modal(Complete_Inperson_Deeds(select.values[0]))

class _Buttons_(discord.ui.View):
    def __init__(self, deed_ID):
        super().__init__(timeout=None)
        self.update_channel_id = int(os.getenv("Discord_Channel_ID"))
        self.deed_id = deed_ID
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def Accept_Condition (self, interaction: discord.Interaction, button: discord.ui.Button):
        bot_logger.info(f"Accept button clicked by {interaction.user.name} for deed {self.deed_id}")
        print("DEED ID: ", self.deed_id)
        v_stmt = select(Tutor).where(Tutor.Discord_ID == interaction.user.name)
        Current_Tutor = session.execute(v_stmt).scalars().first()
        if(Current_Tutor == None):
            bot_logger.warning(f"User {interaction.user.name} is not a tutor, cannot accept deed {self.deed_id}")
            interaction.response.send_message("You are not a tutor youy cannot claim this deed", ephemeral=True)
            return
        stmt = select(Deeds).where(Deeds.ID == int(self.deed_id))
        Deed = session.execute(stmt).scalars().first()
        if(Deed.Current_Status == DEED_STATUS.UNCLAIMED):
            bot_logger.info(f"Deed {self.deed_id} is unclaimed, proceeding with acceptance by {interaction.user.name}")
            CHECK_STMT = select(Deeds).where(
                Deeds.Assigned_Tutor == str(interaction.user.name),
                Deeds.Current_Status == DEED_STATUS.ACCEPTED
            )
            res = session.execute(CHECK_STMT).scalars().first()
            if(res != None):
                bot_logger.warning(f"User {interaction.user.name} already has an uncompleted deed, cannot accept deed {self.deed_id}")
                await interaction.response.send_message("You have an uncompleted deed you cannot accept this one", ephemeral=True)
            else:
                bot_logger.info(f"User {interaction.user.name} has no uncompleted deeds, accepting deed {self.deed_id}")
                Deed.Assigned_Tutor = str(interaction.user.name) 
                Deed.Current_Status = DEED_STATUS.ACCEPTED
                session.commit()
                bot_logger.info(f"Deed {self.deed_id} successfully claimed by {interaction.user.name}")
                await interaction.response.send_message("You have accepted the deed", ephemeral=True)
        elif(Deed.Current_Status == DEED_STATUS.COMPLETED):
            bot_logger.warning(f"Deed {self.deed_id} has already been completed, cannot be accepted by {interaction.user.name}")
            await interaction.response.send_message(f"Unfortunately the deed has already been completed", ephemeral=True)
        elif(Deed.Current_Status == DEED_STATUS.ACCEPTED):
            bot_logger.warning(f"Deed {self.deed_id} has already been claimed by {Deed.Assigned_Tutor}, cannot be accepted by {interaction.user.name}")
            await interaction.response.send_message(f"Unfortunately the deed has already been claimed by {Deeds.Assigned_Tutor}", ephemeral=True)
            

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def Decline_Condition(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot_logger.info(f"Decline button clicked by {interaction.user.name} for deed {self.deed_id}")
        await interaction.response.send_message("You have rejected the deed", ephemeral=True)
        stmt = select(Announced_Deeds).where(Announced_Deeds.Deed_ID == self.deed_id)
        result = session.execute(stmt).scalars().first()
        if(result):
            return
        stmt = select(Deeds).where(Deeds.ID == self.deed_id)
        deed = session.execute(stmt).scalars().all()
        Update_Emded = discord.Embed(
            title="Unclaimed Deed",
            description=f"{deed.Creator} requires help with {deed.Course_Name} ",
            color=discord.Color.red() 
        )
        Update_Emded.add_field(name="Original Message", value=f"{deed.Original_Message}", inline=False)
        Update_Emded.add_field(name="Deed ID: ", value=f"{deed.ID}", inline=False)
        Update_Emded.set_author(name="Deed Informer")
        view = _Buttons_(deed.ID)
        self.update_channel = interaction.client.fetch_channel(self.update_channel_id)
        if self.update_channel:
            bot_logger.info(f"Sending unclaimed deed {deed.ID} to channel {self.update_channel_id}")
            await self.update_channel.send(embed=Update_Emded, view=view)
            Deed_Announcement = Announced_Deeds(Deed_ID=deed.ID)
            session.add(Deed_Announcement)
            session.commit()
        else:
            bot_logger.error(f"Channel {self.update_channel_id} is not available")
            print("Channel Not avaliable", self.update_channel)

class Complete_Inperson_Deeds(discord.ui.Modal, title="Complete Deeds"):
    def __init__(self, course):
        super().__init__(timeout=None)
        self.course = course

    Topics_Covered = discord.ui.TextInput(label="Enter the topics covered during the session", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        bot_logger.info(f"In-person deed form submitted by {interaction.user.name} for course {self.course}")
        User_Name = interaction.user.name
        topic_covered = self.Topics_Covered.value
        stmt = select(Tutor).where(Tutor.Discord_ID == User_Name)
        Current_Tutor = session.execute(stmt).scalars().first()
        if(Current_Tutor):
            bot_logger.info(f"User {User_Name} is a tutor, proceeding with in-person deed completion") 
            Deed_ID = current_milli_time()
            Deed_Logs_ID = current_milli_time()
            New_deeds = Deeds(
                ID=Deed_ID,
                Creator=User_Name,
                Course_Name=self.course,
                Assigned_Tutor=User_Name,
                Created_Time=datetime.now(),
                Original_Message=topic_covered,
                Current_Status =  DEED_STATUS.COMPLETED
            )
            Deed_Log = Deeds_Logs(
                ID=Deed_Logs_ID,
                Deed_ID=Deed_ID,
                Log_Time=datetime.now(),
                Assigned_Tutor=User_Name,
                Student=User_Name,
                Topic_Covered=topic_covered         
            )
            session.add(New_deeds)
            session.add(Deed_Log)
            stmt = select(CurrentPoints).where(CurrentPoints.Discord_ID == Current_Tutor.Discord_ID)
            Current_Points = session.execute(stmt).scalars().first()
            bot_logger.info(f"In-person deed {Deed_ID} completed by tutor {Current_Tutor.Discord_ID}")
            if(Current_Points):
                bot_logger.info(f"Updating points for tutor {Current_Tutor.Discord_ID}")
                Current_Points.Deeds_Point = Current_Points.Deeds_Point + 1
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
            bot_logger.info(f"Points updated and deed {Deed_ID} logged for tutor {Current_Tutor.Discord_ID}")
        else:
            bot_logger.warning(f"User {User_Name} is not a tutor, cannot complete in-person deed")
            await interaction.response.send_message("You are not a tutor this deed cannot be completed", ephemeral=True)

class Complete_Deeds(discord.ui.Modal, title="Complete Deeds"): 
    Deed_ID = discord.ui.TextInput(label="Deed ID", style=discord.TextStyle.short)
    Topics_Covered = discord.ui.TextInput(label="Enter the topics covered during the session", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        bot_logger.info(f"Online deed form submitted by {interaction.user.name} for deed {self.Deed_ID.value}")
        student = interaction.user.name
        Deed_id = int(self.Deed_ID.value)
        Topic_Covered = self.Topics_Covered.value
        guild =interaction.guild
        v_stmt = select(Tutor).where(Tutor.Discord_ID == student)
        Current_Tutor = session.execute(v_stmt).scalars().first()
        if(Current_Tutor): 
            bot_logger.info(f"User {student} is a tutor, proceeding with online deed completion")
            stmt = select(Deeds).where(Deeds.ID == Deed_id)
            Current_Deed = session.execute(stmt).scalars().first()
            if Current_Tutor.Discord_ID == Current_Deed.Assigned_Tutor: 
                Deed_logs = Deeds_Logs(
                    ID= current_milli_time(),
                    Deed_ID=Deed_id,
                    Log_Time=datetime.now(),
                    Assigned_Tutor = Current_Tutor.Discord_ID,
                    Student = Current_Deed.Creator,
                    Topic_Covered = Topic_Covered
                )
                session.add(Deed_logs)
                Current_Deed.Current_Status = DEED_STATUS.COMPLETED
                stmt = select(CurrentPoints).where(CurrentPoints.Discord_ID == Current_Tutor.Discord_ID)
                Current_Points = session.execute(stmt).scalars().first()
                if(Current_Points):
                    Current_Points.Deeds_Point = Current_Points.Deeds_Point + 1
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
                    bot_logger.info(f"Online deed {Deed_id} completed by tutor {Current_Tutor.Discord_ID}")
                session.commit()
            elif(Current_Tutor.Discord_ID != Current_Deed.Assigned_Tutor):
                await interaction.response.send_message("You did not claim this deed you cannot complete it", ephemeral=True)
                bot_logger.warning(f"User {student} did not claim deed {Deed_id}, cannot complete it")
            elif(Current_Deed.Current_Status == DEED_STATUS.UNCLAIMED):
                await interaction.response.send_message("Please claim the deed before you can complete it", ephemeral=True)
                bot_logger.warning(f"Deed {Deed_id} is unclaimed, user {student} cannot complete it")
        else:
            await interaction.response.send_message("You are not a tutor you cannot run this command", ephemeral=True)
            bot_logger.warning(f"User {student} is not a tutor, cannot complete deed {Deed_id}")    

class Admin(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(
    placeholder="Please select admin powers you will like to use: ",
        options=[
            discord.SelectOption(label="Add a new tutor", value=1),
            discord.SelectOption(label="Delete Tutor", value=2),
            discord.SelectOption(label="Create a new Workshop deed", value=3),
            discord.SelectOption(label="View all tutors and their points", value=4),
            discord.SelectOption(label="Alter tutors point", value=5),
            discord.SelectOption(label="View Logs", value=6)
        ]
    )

    async def on_submit(self, interaction: discord.Interaction, select):
        bot_logger.info(f"Admin option {select.values[0]} selected by {interaction.user.name}")
        await interaction.message.delete()
        if(select.values[0] == "1"):
            print("poop")
            bot_logger.info(f"Sending add new tutor modal to {interaction.user.name}")
            await interaction.response.send_modal(add_new_tutor())
        elif(select.values[0] == "2"):
            bot_logger.info(f"Sending delete tutor modal to {interaction.user.name}")
            await interaction.response.send_modal(Del_tutor())
        elif(select.values[0] == "3"):
            bot_logger.info(f"Sending workshop course list to {interaction.user.name}")
            view = Workshop_Course_List(self.bot)
            await interaction.response.send_message(view=view)
            #Need to add bot it is one of the parameters for the class
        elif(select.values[0] == "4"):
            bot_logger.info(f"Sending view all tutors embed to {interaction.user.name}")
            Current_View = View_All_Tutors
            embed = await Current_View.View_Embed()
            await interaction.response.send_message(embed=embed)
        elif(select.values[0] == "5"):
            bot_logger.info(f"Sending alter tutor points modal to {interaction.user.name}")
            await interaction.response.send_modal(Alter_Tutor_points())
        elif(select.values[0] == "6"):
            bot_logger.info(f"Sending add from files modal to {interaction.user.name}")
            file = discord.File("Deed_Manager.log", filename="Deed_Manager.log")
            await interaction.response.send_message(file=file, ephemeral=True)

class Tutoring_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.view = View()
        self.update_channel_id = int(os.getenv("Discord_Channel_ID"))
        self.update_channel = self.bot.get_channel(self.update_channel_id) 

    @commands.Cog.listener()  
    async def on_ready(self):
        print(f'Logged on as {self.bot.user}!')
        bot_logger.info(f'Bot logged in as {self.bot.user}')
        self.update_channel_id = int(os.getenv("Discord_Channel_ID"))
        self.update_channel = self.bot.get_channel(self.update_channel_id)
        self.Update_Deeds.start()      

    async def cog_unload(self):
        self.Update_Deeds.cancel()

    @discord.app_commands.command(name="info", description="Contains info about the bot")
    async def info(self, interaction: discord.Interaction):
        bot_logger.info(f"Info command invoked by {interaction.user.name}")
        await interaction.response.send_message(info)

    @discord.app_commands.command(name="question", description="This is a function for sending out questions directly to tutors")
    async def question(self, interaction: discord.Interaction):
        self.view = Course_List(self.bot)
        bot_logger.info(f"Question command invoked by {interaction.user.name}")
        await interaction.response.send_message(view=self.view)
    
    @discord.app_commands.command(name="complete_deeds", description="This command is used to complete deeds and to receive the requiste points")
    async def complete_deeds(self, interaction: discord.Interaction):
        bot_logger.info(f"Complete deeds command invoked by {interaction.user.name}")
        await interaction.response.send_message(view=Deeds_List())

    @discord.app_commands.command(name="current_points", description="This command is used to view your current points")
    async def current_points(self, interaction: discord.Interaction):
        user_name = interaction.user.name
        guild = interaction.guild
        stmt =  select(Tutor).where(Tutor.Discord_ID == user_name)
        Current_Tutor = session.execute(stmt).scalars().first()
        print(Current_Tutor)
        bot_logger.info(f"Current points command invoked by {interaction.user.name}")
        if(Current_Tutor):
            bot_logger.info(f"User {user_name} is a tutor, fetching current points")
            if (Current_Tutor.Current_points.Deeds_Point):
                Points_Embed = discord.Embed(
                    title="Current Points",
                    description=f"{Current_Tutor.First_Name} {Current_Tutor.Last_Name} your current points are {Current_Tutor.Current_points.Deeds_Point}",
                    color=discord.Color.blue()  
                )
                target_user = discord.utils.get(guild.members, name=user_name)
                await target_user.send(embed=Points_Embed)
                bot_logger.info(f"Sent current points DM to tutor {user_name}")
                return await interaction.response.send_message("Your Points has been sent to you as a dm", ephemeral=True)
            else:
                bot_logger.info(f"Tutor {user_name} currently has no points")
                return await interaction.response.send_message("You Currently have no points", ephemeral=True)
        else:
            bot_logger.warning(f"User {user_name} is not a tutor, cannot fetch current points")
            return await interaction.response.send_message("Unfortunately you are not a tutor we dont have any records for you", ephemeral=True)

    @discord.app_commands.command(name="leaderboard", description="This command is used to view the current leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        bot_logger.info(f"Leaderboard command invoked by {interaction.user.name}")
        user_name = interaction.user.name
        stmt =  select(Tutor).where(Tutor.Discord_ID == user_name)
        Current_Tutor = session.execute(stmt).scalars().first()
        if(Current_Tutor):
            bot_logger.info(f"User {user_name} is a tutor, fetching leaderboard")
            stmt = select(Tutor).join(Tutor.Current_points).order_by(CurrentPoints.Deeds_Point.asc())
            Current_tutors = session.execute(stmt).scalars().all()
            Points_Embed = discord.Embed(
                title="Leaderboard",
                color=discord.Color.blue()  
            )
            for tutor in Current_tutors:
                Points_Embed.add_field(name=f"{tutor.First_Name} {tutor.Last_Name}: ", value=f"{tutor.Current_points.Deeds_Point}", inline=False)
            await interaction.response.send_message(embed=Points_Embed)
            bot_logger.info(f"Sent leaderboard embed to tutor {user_name}")
        else: 
            bot_logger.warning(f"User {user_name} is not a tutor, cannot fetch leaderboard")
            return await interaction.response.send_message("Unfortunately you are not a tutor we dont have any records for you")

    @discord.app_commands.command(name="view_uncompleted_deeds", description="This command is used to view the ids of you current uncompleted deeds")
    async def view_uncompleted_deeds(self, interaction: discord.Interaction):
        user_name = interaction.user.name
        stmt =  select(Tutor).where(Tutor.Discord_ID == user_name)
        Current_Tutor = session.execute(stmt).scalars().first()
        bot_logger.info(f"View uncompleted deeds command invoked by {interaction.user.name}")
        if(Current_Tutor):
            stmt =  select(Deeds).where(Deeds.Assigned_Tutor == Current_Tutor.Discord_ID, Deeds.Current_Status != DEED_STATUS.COMPLETED)
            Current_Deeds = session.execute(stmt).scalars().all()
            bot_logger.info(f"User {user_name} is a tutor, fetching uncompleted deeds")
            if(len(Current_Deeds) != 0):
                Deeds_Embed = discord.Embed(
                    title="Uncompleted Deeds",
                    color=discord.Color.blue()
                )
                for deeds in Current_Deeds:
                    Deeds_Embed.add_field(name=f"{Current_Tutor.First_Name} {Current_Tutor.Last_Name}: ", value=f"{deeds.ID}")
                    bot_logger.info(f"Added deed {deeds.ID} to uncompleted deeds embed for tutor {user_name}")
                bot_logger.info(f"Sent uncompleted deeds embed to tutor {user_name}")
                await interaction.response.send_message(embed=Deeds_Embed)
            else:
                bot_logger.info(f"Tutor {user_name} has no uncompleted deeds")
                return await interaction.response.send_message("All your deeds are currently complete")  
        else:
            bot_logger.warning(f"User {user_name} is not a tutor, cannot fetch uncompleted deeds")
            return await interaction.response.send_message("Unfortunately you are not a tutor we dont have any records for you")

    @discord.app_commands.command(name="admin_panel", description="This command is only meant to be used by the admin")
    async def admin_panel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            bot_logger.warning(f"User {interaction.user.name} attempted to access admin panel without permissions")
            return await interaction.response.send_message("You don't have admin permissions to use this command.")
        else:
            bot_logger.info(f"Admin panel command invoked by {interaction.user.name}")
            await interaction.response.send_message(view=Admin(self.bot))
    
    @discord.app_commands.command(name="data_entry_from_csv", description="This command is only meant to be used by the admin")
    async def data_entry_from_csv(self, interaction: discord.Interaction, file:discord.Attachment):
        if not interaction.user.guild_permissions.administrator:
            bot_logger.warning(f"User {interaction.user.name} attempted to use data entry from csv without permissions")
            return await interaction.followup.send("You don't have admin permissions to use this command.")
        bot_logger.info(f"Data entry from csv command invoked by {interaction.user.name}")
        if not file.filename.endswith('.csv'):
            bot_logger.error(f"File {file.filename} is not a CSV file, cannot proceed with data entry")
            return await interaction.followup.send("Please upload a valid CSV file.")
        if not os.path.exists('./Uploads'):
            os.makedirs('./Uploads')
        
        file_path = f"./Uploads/{file.filename}"
        View = Add_From_Files(file_path)
        bot_logger.info(f"Saving uploaded file {file.filename} to {file_path}")
        await file.save(file_path)
        bot_logger.info(f"File {file.filename} saved successfully, proceeding with data entry")
        await interaction.response.send_message(view=View)

    @tasks.loop(minutes=15)
    async def Update_Deeds(self):
        bot_logger.info("Running Update_Deeds task")
        stmt = select(Deeds).where(
        func.date(Deeds.Created_Time) == date.today() )
        Todays_Deeds = session.execute(stmt).scalars().all()
        for deed in Todays_Deeds:
            Total_minutes = ((
                deed.Created_Time.hour * 60 + 
                deed.Created_Time.minute))
            if(deed.Current_Status == DEED_STATUS.UNCLAIMED):
                stmt = select(Announced_Deeds).where(Announced_Deeds.Deed_ID == deed.ID)
                result = Todays_Deeds = session.execute(stmt).scalars().first()
                if(Total_minutes > 15 and result is None):
                    bot_logger.info(f"Deed {deed.ID} has been unclaimed for over 15 minutes, announcing to all tutors")
                    Update_Emded = discord.Embed(
                        title="Unclaimed Deed",
                        description=f"{deed.Creator} requires help with {deed.Course_Name} ",
                        color=discord.Color.red() 
                    )
                    Update_Emded.add_field(name="Original Message", value=f"{deed.Original_Message}", inline=False)
                    Update_Emded.add_field(name="Deed ID: ", value=f"{deed.ID}", inline=False)
                    Update_Emded.set_author(name="Deed Informer")
                    self.view = _Buttons_(deed.ID)
                    if self.update_channel:
                        bot_logger.info(f"Sending unclaimed deed {deed.ID} to channel {self.update_channel_id}")
                        await self.update_channel.send(embed=Update_Emded, view=self.view)
                        Deed_Announcement = Announced_Deeds(Deed_ID=deed.ID)
                        session.add(Deed_Announcement)
                        session.commit()
                    else:
                        bot_logger.error(f"{self.update_channel} self.update_channel")
                        print("Channel Not avaliable", self.update_channel)
            elif(Total_minutes > 180 and deed.Current_Status != DEED_STATUS.COMPLETED):
                bot_logger.info(f"Deed {deed.ID} has been uncompleted for over 3 hours, marking as completed")
                deed.Current_Status == DEED_STATUS.COMPLETED
                 
class Tutoring_Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        intents.message_content = True 
        super().__init__(command_prefix="$", intents=intents)
        bot_logger.info("Bot initialized with intents")

    async def setup_hook(self):
        await self.add_cog(Tutoring_Cog(self))
        await self.tree.sync()

client = Tutoring_Bot()
client.run(os.getenv("Discord_Token"))