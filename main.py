import discord
from discord.ext import commands
import requests
import json
import re
import asyncio
import frames
import os

#Client
client = discord.Client()
client = commands.Bot(command_prefix = '$')

def get_quote():
        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)
        quote = json_data[0]['q']
        return quote

@client.event
async def on_ready():
        print(f"Bot has logged in as {client.user}")

@client.command(aliases = ['hm', 'hg'])
async def hangman(ctx):
        quote = get_quote()
        quote = quote.lower()
        quote_cleared = re.sub(r'[^A-Za-z ]', '', quote)
        new_quote = re.sub('[A-Za-z]','-',quote_cleared)

        await ctx.send(frames.hangman_frames(new_quote , 0))
        guessed = False
        guessed_letters = []
        guessed_quotes = []
        tries = 6      

        while not guessed and tries > 0:
                def check(msg):
                        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower()
                try:
                        message = await client.wait_for("message", check=check, timeout=60)
                except asyncio.TimeoutError:
                        print("")
                        await ctx.send("Sorry, you didn't reply in time!")
                        ctx.send("The word was " + quote + ". Maybe next time!")
                        break
                guess = message.content
                print("\nPlayer guessed: " + guess)
                if len(guess) == 1 and guess.isalpha():
                        if guess in guessed_letters:
                                await ctx.send("You already guessed this letter")
                                print("Player had already guessed this letter")
                        elif guess not in quote_cleared:
                                await ctx.send(guess + " is not in quote.")
                                tries -= 1
                                print("Player's guess \" " + guess + " \" was incorrect. \nPlayer has " + str(tries) + " tries left.")
                                guessed_letters.append(guess)
                        else: 
                                await ctx.send("Good job \"" + guess + "\" is in the quote")
                                print("Player's guess \"" + guess + "\" was correct. \nPlayer has " + str(tries) + " tries left.")
                                guessed_letters.append(guess)
                                word_as_list = list(new_quote)
                                indices = [i for i, letter in enumerate(quote_cleared) if letter == guess]
                                for index in indices:
                                        word_as_list[index] = guess
                                new_quote = "".join(word_as_list)
                                if "-" not in new_quote:
                                        guessed = True
                elif len(guess) == len(quote_cleared):
                        if guess in guessed_quotes:
                                await ctx.send("You already guessed this quote")
                                print("Player had already guessed this quote.")
                        elif guess != quote_cleared:
                                await ctx.send("Your guess \"" + guess + "\" was incorrect try again")
                                tries -= 1
                                print("Player's guess \"" + guess + "\" was incorrect. \nPlayer has " + str(tries) + " tries left.")
                                guessed_quotes.append(guess)
                        else:
                                guessed = True
                                new_quote = quote_cleared
                                print("Player's guess \"" + guess + "\" was correct. \nPlayer still has " + str(tries) + " tries left.")
                else:
                        await ctx.send("Answer not valid")
                        print("Player's result is not valid")
                await ctx.send(frames.hangman_frames(new_quote , 6 - tries))
                print("\nQuote: \t\t\t" + quote_cleared + "\nCurrent State of Quote: " + new_quote)

        if guessed:
                await ctx.send("Congrats, you guessed the word! You win!")
                print("Game is finished: Result: Win")
        else:
                await ctx.send("Sorry, you ran out of tries. The word was " + quote_cleared + ". Maybe next time!")
                print("Game is finished: Result: Loss")

client.run(os.getenv('TOKEN'))