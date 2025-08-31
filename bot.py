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
from models import Tutor, CurrentPoints, Availability, DAYS_OF_THE_WEEK, DEED_STATUS, Deeds, Announced_Deeds, Deeds_Logs, Tutored_Courses, Courses
from Admin import add_new_tutor, Del_tutor, Alter_Tutor_points, Workshop_Course_List, Create_Workshop_deeds, Claim_Workshop_deed, Complete_Workshop_Deeds

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def current_milli_time():
    return round(t.time() * 1000)

def get_user(Current_time, Day_of_the_week, courses):
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
        Current_time = time(15,30,00)
        Day_of_the_week = 3
        tutors = get_user(Current_time=Current_time, Day_of_the_week=Day_of_the_week, courses=self.course)
        print("Tutors: ", tutors)
        if(len(tutors) == 0):
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
                return
            else:
                print("Channel Not avaliable", self.update_channel)
                return
        for tutor_name in tutors:
            target_user = discord.utils.get(guild.members, name=tutor_name)
            print("Target User: ", target_user)
            if target_user:
                try:
                    await target_user.send(embed=embed, view=self.view)
                    await interaction.response.send_message(f"A tutor has been made aware of your question and will be reaching out. Course name: {self.course}", ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message(f"Could not send DM to {target_user.name}. They may have DMs disabled or blocked the bot.")
            else:
                await interaction.response.send_message("User could not be found")
        
class Course_List(discord.ui.View):
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
        print("Select: ", select.values[0])
        if(select.values[0] == "1"):
            await interaction.response.send_modal(Complete_Deeds())
        elif(select.values[0] == "2"):
            print ("poop")
            await interaction.response.send_message(view=Complete_Deeds_Course_List())
        elif(select.values[0] == "3"):
            await interaction.response.send_modal(Complete_Deeds())

class Complete_Deeds_Course_List(discord.ui.View):
    @discord.ui.select(
        placeholder="Please select the course you turtored: ",
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

    async def on_submit(self, interaction: discord.Interaction, select):
        print("Select: ", select.values[0])
        await interaction.response.send_modal(Complete_Inperson_Deeds(select.values[0]))

class _Buttons_(discord.ui.View):
    def __init__(self, deed_ID):
        super().__init__(timeout=None)
        self.update_channel_id = int(os.getenv("Discord_Channel_ID"))
        self.deed_id = deed_ID
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def Accept_Condition (self, interaction: discord.Interaction, button: discord.ui.Button):
        print("DEED ID: ", self.deed_id)
        stmt = select(Deeds).where(Deeds.ID == int(self.deed_id))
        Deed = session.execute(stmt).scalars().first()
        if(Deed.Current_Status == DEED_STATUS.UNCLAIMED):
            CHECK_STMT = select(Deeds).where(
                Deeds.Assigned_Tutor == str(interaction.user.name),
                Deeds.Current_Status == DEED_STATUS.ACCEPTED
            )
            res = session.execute(CHECK_STMT).scalars().first()
            if(res != None):
                await interaction.response.send_message("You have an uncompleted deed you cannot accept this one", ephemeral=True)
            else:
                Deed.Assigned_Tutor = str(interaction.user.name) 
                Deed.Current_Status = DEED_STATUS.ACCEPTED
                session.commit()
                await interaction.response.send_message("You have accepted the deed", ephemeral=True)
        elif(Deed.Current_Status == DEED_STATUS.COMPLETED):
            await interaction.response.send_message(f"Unfortunately the deed has already been completed", ephemeral=True)
        elif(Deed.Current_Status == DEED_STATUS.ACCEPTED):
            await interaction.response.send_message(f"Unfortunately the deed has already been claimed by {Deeds.Assigned_Tutor}", ephemeral=True)
            

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def Decline_Condition(self, interaction: discord.Interaction, button: discord.ui.Button):
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
            await self.update_channel.send(embed=Update_Emded, view=view)
            Deed_Announcement = Announced_Deeds(Deed_ID=deed.ID)
            session.add(Deed_Announcement)
            session.commit()
        else:
            print("Channel Not avaliable", self.update_channel)

class Complete_Inperson_Deeds(discord.ui.Modal, title="Complete Deeds"):
    def __init__(self, course):
        super().__init__(timeout=None)
        self.course = course

    Topics_Covered = discord.ui.TextInput(label="Enter the topics covered during the session", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        User_Name = interaction.user.name
        topic_covered = self.Topics_Covered.value
        stmt = select(Tutor).where(Tutor.Discord_ID == User_Name)
        Current_Tutor = session.execute(stmt).scalars().first()
        if(Current_Tutor): 
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
            session.commit()
        else:
            await interaction.response.send_message("You are not a tutor this deed cannot be completed", ephemeral=True)

class Complete_Deeds(discord.ui.Modal, title="Complete Deeds"): 
    Deed_ID = discord.ui.TextInput(label="Deed ID", style=discord.TextStyle.short)
    Topics_Covered = discord.ui.TextInput(label="Enter the topics covered during the session", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        student = interaction.user.name
        Deed_id = int(self.Deed_ID.value)
        Topic_Covered = self.Topics_Covered.value
        guild =interaction.guild
        v_stmt = select(Tutor).where(Tutor.Discord_ID == student)
        Current_Tutor = session.execute(v_stmt).scalars().first()
        if(Current_Tutor): 
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
                session.commit()
            elif(Current_Tutor.Discord_ID != Current_Deed.Assigned_Tutor):
                await interaction.response.send_message("You did not claim this deed you cannot complete it", ephemeral=True)
            elif(Current_Deed.Current_Status == DEED_STATUS.UNCLAIMED):
                await interaction.response.send_message("Please claim the deed before you can complete it", ephemeral=True)    

class Admin(discord.ui.View):
    @discord.ui.select(
        placeholder="Please select admin powers you will like to use: ",
        options=[
            discord.SelectOption(label="Add a new tutor", value=1),
            discord.SelectOption(label="Delete Tutor", value=2),
            discord.SelectOption(label="Create a new Workshop deed", value=3),
            discord.SelectOption(label="View all tutors and their points", value=4),
            discord.SelectOption(label="Alter tutors point", value=5),
        ]
    )

    async def on_submit(self, interaction: discord.Interaction, select):
        print("Select: ", select.values[0])
        if(select.values[0] == 1):
            await interaction.response.send_modal(add_new_tutor())
        elif(select.values[0] == 2):
            await interaction.response.send_modal(Del_tutor())
        elif(select.values[0] == 3):
            await interaction.response.send_modal(Workshop_Course_List())
            #Need to add bot it is one of the parameters for the class
        elif(select.values[0] == 4):
            stmt = select(Tutor).join(Tutor.Current_points)
            All_Tutors = session.execute(stmt).scalars().all()
            tutors_embed = discord.embed(
                title="Current Tutors",
                description=f"Here is a list of current tutors",
                color=discord.Color.blue() 
            )
            for tutor in All_Tutors:
                tutors_embed.add_field(name=f"{tutor.First_Name} {tutor.Last_Name}: ", value=f"{tutor.Current_points.Deeds_Point}", inline=True)
            await interaction.response.send_message(embed=tutors_embed)
        elif(select.values[0] == 5):
            await interaction.response.send_modal(Alter_Tutor_points())





class Tutoring_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.view = View()
        self.update_channel_id = int(os.getenv("Discord_Channel_ID"))
        self.update_channel = self.bot.get_channel(self.update_channel_id) 

    @commands.Cog.listener()  
    async def on_ready(self):
        print(f'Logged on as {self.bot.user}!')
        self.update_channel_id = int(os.getenv("Discord_Channel_ID"))
        self.update_channel = self.bot.get_channel(self.update_channel_id)
        self.Update_Deeds.start()      

    async def cog_unload(self):
        self.Update_Deeds.cancel()

    @discord.app_commands.command(name="question", description="This is a function for sending out questions directly to tutors")
    async def question(self, interaction: discord.Interaction):
        self.view = Course_List(self.bot)
        await interaction.response.send_message(view=self.view)
    
    @discord.app_commands.command(name="complete_deeds", description="This command is used to complete deeds and to receive the requiste points")
    async def complete_deeds(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=Deeds_List())

    @discord.app_commands.command(name="current_points", description="This command is used to view your current points")
    async def current_points(self, interaction: discord.Interaction):
        user_name = interaction.user.name
        guild = interaction.guild
        stmt =  select(Tutor).where(Tutor.Discord_ID == user_name)
        Current_Tutor = session.execute(stmt).scalars().first()
        print(Current_Tutor)
        if(Current_Tutor):
            if (Current_Tutor.Current_points.Deeds_Point):
                Points_Embed = discord.Embed(
                    title="Current Points",
                    description=f"{Current_Tutor.First_Name} {Current_Tutor.Last_Name} your current points are {Current_Tutor.Current_points.Deeds_Point}",
                    color=discord.Color.blue()  
                )
                target_user = discord.utils.get(guild.members, name=user_name)
                await target_user.send(embed=Points_Embed)
            else:
                return interaction.response.send_message("You Currently have no points", ephermal=True)
        else:
            return interaction.response.send_message("Unfortunately you are not a tutor we dont have any records for you", ephermal=True)

    @discord.app_commands.command(name="leaderboard", description="This command is used to view the current leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        user_name = interaction.user.name
        stmt =  select(Tutor).where(Tutor.Discord_ID == user_name)
        Current_Tutor = session.execute(stmt).scalars().first()
        if(Current_Tutor):
            stmt = select(Tutor).join(Tutor.Current_points).order_by(CurrentPoints.Deeds_Point.asc())
            Current_tutors = session.execute(stmt).scalars().all()
            Points_Embed = discord.Embed(
                title="Leaderboard",
                color=discord.Color.blue()  
            )
            for tutor in Current_tutors:
                Points_Embed.add_field(name=f"{tutor.First_Name} {tutor.Last_Name}: ", value=f"{tutor.Current_points.Deeds_Point}", inline=True)
            await interaction.response.send_message(embed=Points_Embed)
        else: 
            return interaction.response.send_message("Unfortunately you are not a tutor we dont have any records for you")

    @discord.app_commands.command(name="view_uncompleted_deeds", description="This command is used to view the ids of you current uncompleted deeds")
    async def view_uncompleted_deeds(self, interaction: discord.Interaction):
        user_name = interaction.user.name
        stmt =  select(Tutor).where(Tutor.Discord_ID == user_name)
        Current_Tutor = session.execute(stmt).scalars().first()
        if(Current_Tutor):
            stmt =  select(Deeds).where(Deeds.Assigned_Tutor == Current_Tutor.Discord_ID, Deeds.Current_Status != DEED_STATUS.COMPLETED)
            Current_Deeds = session.execute(stmt).scalars().all()
            if(len(Current_Deeds) != 0):
                Deeds_Embed = discord.Embed(
                    title="Uncompleted Deeds",
                    color=discord.Color.blue()
                )
                for deeds in Current_Deeds:
                    Deeds_Embed.add_field(name=f"{Current_Tutor.First_Name} {Current_Tutor.Last_Name}: ", value=f"{deeds.ID}")
                await interaction.response.send_message(embed=Deeds_Embed)
            else:
              return await interaction.response.send_message("All your deeds are currently complete")  
        else:
            return await interaction.response.send_message("Unfortunately you are not a tutor we dont have any records for you")

    @discord.app_commands.command(name="admin_panel", description="This command is only meant to be used by the admin")
    async def admin_panel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You don't have admin permissions to use this command.")
        else:
            await interaction.response.send_message(view=Admin())
    @tasks.loop(minutes=15)
    async def Update_Deeds(self):
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
                        await self.update_channel.send(embed=Update_Emded, view=self.view)
                        Deed_Announcement = Announced_Deeds(Deed_ID=deed.ID)
                        session.add(Deed_Announcement)
                        session.commit()
                    else:
                        print("Channel Not avaliable", self.update_channel)
            elif(Total_minutes > 180 and deed.Current_Status != DEED_STATUS.COMPLETED):
                deed.Current_Status == DEED_STATUS.COMPLETED
                 
class Tutoring_Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        intents.message_content = True 
        super().__init__(command_prefix="$", intents=intents)

    async def setup_hook(self):
        await self.add_cog(Tutoring_Cog(self))
        await self.tree.sync()

client = Tutoring_Bot()
client.run(os.getenv("Discord_Token"))