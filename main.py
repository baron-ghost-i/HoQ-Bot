import os
import discord
import asyncio
import aiohttp
import json
import pymongo
from discord.ext import commands, tasks
from utils.slash import Slashcommands
from utils.utils import guildid

token = os.getenv('Token')
intents = discord.Intents.default()
intents.members = True
intents.typing = False

class HoQBot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.session = None
		self.db = pymongo.MongoClient(os.getenv("mongourl"))["HoQ-Bot"]
		for i in os.scandir(path = "cogs"):
			if i.name.endswith(".py"):
				self.load_extension(f"cogs.{i.name[:-3]}")
	
	async def on_connect(self):
		self.session = aiohttp.ClientSession()

	async def on_interaction(self, interaction: discord.Interaction):
		if interaction.type != discord.InteractionType.application_command:
			return
		slash = Slashcommands(self, interaction)
		try:
			await slash.execute()
		except Exception as e:
			raise e
		
	async def on_ready(self):
		c = self.get_channel(850039242481991703)
		await asyncio.sleep(5)
		await c.send("Bot online")

		for i in self.guilds:
			try:
				self.db["Guild settings"].insert_one({"_id": id, "dadmode": False, "default role": None, "autoresponder": False})
			except:
				pass

	async def on_guild_join(self, guild):
		id = guildid(guild.id)
		try:
			self.db["Guild settings"].insert_one({"_id": id, "dadmode": False, "default role": None, "autoresponder": False})
		except:
			pass

	async def on_guild_remove(self, guild):
		id = guildid(guild.id)
		try:
			self.db["Guild settings"].delete_one({"_id": id})
		except:
			pass

	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.reply(embed = discord.Embed(description = f"Missing argument: {error.param.name}", color = discord.Color.red()))
		
		elif isinstance(error, commands.CommandInvokeError):
			err = error.original
			if isinstance(err, discord.HTTPException):
				await ctx.reply(embed = discord.Embed(description = f"{err.status} Error: {err.text}", color = discord.Color.red()))
			else:
				raise err
		
		elif isinstance(error, commands.PrivateMessageOnly):
			await ctx.reply(embed = discord.Embed(description = "Use this command in DMs!", color = discord.Color.red()))
		
		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.reply(embed = discord.Embed(description = f"Command is on cooldown! Try again after {round(error.retry_after, 2)} seconds", color = discord.Color.red()))
		
		elif isinstance(error, commands.NotOwner) or isinstance(error, commands.MissingPermissions):
			await ctx.reply(embed = discord.Embed(description = "You do not have the permission to use this command!", color = discord.Color.red()))
		
		elif isinstance(error, commands.CommandNotFound):
			pass
		
		elif isinstance(error, commands.BadUnionArgument):
			await ctx.reply(embed = discord.Embed(description = "Error: conversion failed, please check the input provided.", color = discord.Color.red()))
		
		elif isinstance(error, commands.UserInputError):
			await ctx.reply(embed = discord.Embed(description = f"Input error: {error}", color = discord.Color.red()))
		
		elif isinstance(error, commands.UserNotFound):
			await ctx.reply(embed = discord.Embed(description = "Error: User not found", color = discord.Color.red()))
		
		elif isinstance(error, commands.CheckFailure):
			await ctx.reply(embed = discord.Embed(description = f"{error}", color = discord.Color.red()))
			
bot = HoQBot(command_prefix = ("h!", "hoq ", "Hoq ", "h?", "h.", "H!", "H?", "H."), max_messages = 2048, activity = discord.Activity(type = discord.ActivityType.watching, name = "for h!"),  allowed_mentions = discord.AllowedMentions(replied_user = False), intents = intents)

def isme(ctx):
		return ctx.author.id == 586088176037265408

@bot.command()
@commands.check(isme)
async def reload(ctx, *, extension = None):
	try:
		if extension != None:
			try:
				ctx.bot.reload_extension(name = f"cogs.{extension}")
			except:
				await ctx.send("Extension not found")
		else:
			for i in list(ctx.bot.extensions):
				ctx.bot.reload_extension(name = i)
		await ctx.send("Reloaded!")
	except:
		raise

@bot.command()
@commands.check(isme)
async def guilds(ctx: commands.Context):
	guilds = [i.name for i in ctx.bot.guilds]
	await ctx.send("\n".join(guilds))

bot.run(token)