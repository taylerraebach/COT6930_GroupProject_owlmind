from dotenv import dotenv_values
from owlmind.discord import DiscordBot
from owlmind.botengine import SimpleBrain
import random
import time
import discord
from discord.ext import tasks, commands
import openai
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Placeholder functions for additional features
def generate_quiz(topic):
    # Example: Generate a simple quiz based on the topic
    quizzes = {
        'acids_and_bases': [
            {"question": "What is the pH of a neutral solution?", "answer": "7"},
            {"question": "What is the difference between an acid and a base?", "answer": "An acid donates protons, while a base accepts protons."},
        ],
        'chemical_reactions': [
            {"question": "What is a combustion reaction?", "answer": "A chemical reaction where a substance combines with oxygen and releases energy."},
            {"question": "Balance the equation: CH₄ + O₂ → CO₂ + H₂O", "answer": "CH₄ + 2O₂ → CO₂ + 2H₂O"},
        ],
    }
    return random.choice(quizzes.get(topic, []))

def summarize_material(topic):
    # Example: Summarize material based on the topic
    summaries = {
        'thermodynamics': "Thermodynamics is the study of energy and heat. The first law states that energy can neither be created nor destroyed.",
        'stoichiometry': "Stoichiometry involves calculating reactants and products in chemical reactions, based on balanced equations.",
    }
    return summaries.get(topic, "No summary available for this topic.")

def send_study_reminder(user):
    # Example: Send study reminder
    return f"Reminder: Don't forget to study today, {user}! Focus on your chemistry topics!"

def generate_flashcards(text):
    # Example: Generate flashcards from text
    flashcards = []
    # Extract key concepts/terms from the text (simplified for this prototype)
    terms = text.split()[:5]  # Just a simple example, you can use NLP to extract more meaningful terms
    for term in terms:
        flashcards.append(f"Q: What is {term}? \nA: [Answer here]")
    return flashcards

def save_session_transcript(messages):
    # Example: Save session chat as text (could be later converted to PDF)
    session_text = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])
    return session_text

# Onboarding feature - greeting and role assignment
async def on_member_join(member):
    # Assign the "Student" role to new users
    role = discord.utils.get(member.guild.roles, name="Student")
    if role:
        await member.add_roles(role)
    await member.send(f"Welcome to the study bot! Type !help to get started.")

# Initialize Discord client
intents = discord.Intents.default()
intents.members = True  # Needed for member join events
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

# Scheduled task for study reminders
scheduler = AsyncIOScheduler()
@scheduler.scheduled_job('interval', seconds=3600)  # Remind every hour
async def scheduled_reminder():
    # Here you could remind users based on their preferences or schedule
    for user in bot.users:
        if isinstance(user, discord.User):  # Avoid bots
            await user.send("Study Reminder: Don't forget to review your chemistry topics!")

# Define bot commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    scheduler.start()  # Start scheduled tasks like reminders

# Q&A command: User requests information on a topic
@bot.command(name='q')
async def q_and_a(ctx, *, topic: str):
    # Summarize material for the topic
    response = summarize_material(topic)
    await ctx.send(response)

# Quiz command: Generate a personalized quiz for a topic
@bot.command(name='quiz')
async def quiz(ctx, *, topic: str):
    quiz = generate_quiz(topic)
    if quiz:
        await ctx.send(f"Question: {quiz['question']}")
    else:
        await ctx.send("Sorry, I couldn't find a quiz for that topic.")

# Flashcards command: Generate chemistry flashcards from text
@bot.command(name='flashcards')
async def flashcards(ctx, *, text: str):
    flashcards = generate_flashcards(text)
    for card in flashcards:
        await ctx.send(card)

# Help command: Provide help for a specific topic
@bot.command(name='help')
async def help_command(ctx, *, topic: str = None):
    if topic:
        # Provide specific help based on topic
        await ctx.send(f"Providing help on {topic}. Here's a summary...")
    else:
        # Provide general help
        await ctx.send("Use !q [topic] for Q&A, !quiz [topic] for a quiz, !flashcards for flashcards.")

# Session transcript command: Export chat log
@bot.command(name='export')
async def export_session(ctx):
    # Fetch previous messages
    messages = await ctx.channel.history(limit=100).flatten()
    session_text = save_session_transcript(messages)
    # Save as text (PDF generation can be added later)
    with open('session_log.txt', 'w') as f:
        f.write(session_text)
    await ctx.send("Session exported successfully!")

# Handle new member join event for onboarding
@client.event
async def on_member_join(member):
    await on_member_join(member)

# Run the bot
if __name__ == '__main__':
    # Load token from .env
    config = dotenv_values(".env")
    TOKEN = config['TOKEN']
    
    # Run the Discord bot
    bot.run(TOKEN)

