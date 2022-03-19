import discord
import json
import random
import asyncio
import datetime
from discord.ext import commands

class Misc(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command()
	async def ping(self, ctx):
		ping = round(self.bot.latency*1000)
		await ctx.channel.send(f"Ping: {ping} ms")
		
	@commands.command()
	async def invite(self, ctx):
		'''For inviting the bot, or joining the HoQ-QFC Joint Server'''
		embd = discord.Embed(color = 0x00d5ff)
		embd.set_author(name = "HoQ Bot", icon_url = "https://media.discordapp.net/attachments/850039242481991703/850043262232559676/HoQ.png")
		embd.add_field(name = "Bot Invitation", value = "[Invite HoQ Bot!](https://discord.com/api/oauth2/authorize?client_id=849171433762193419&permissions=8&scope=bot%20applications.commands)", inline = False)
		embd.add_field(name = "Server Invite", value = "[Join HoQ!](https://discord.com/invite/z2VP7SA)", inline = False)
		embd.set_footer(text = "Not a public bot, to be used on HoQ and related servers only")
		await ctx.channel.send(embed = embd)

	@commands.command()
	@commands.cooldown(1, 10, commands.BucketType.default)
	async def xkcd(self, ctx, *, args = None):
		'''Shows an xkcd comic'''
		try:
			url1 = "https://xkcd.com/info.0.json"
			async with self.bot.session.get(url1) as req1:
				stat1 = req1.status
				jsonobj = await req1.text()
			assert stat1 == 200
			content1 = json.loads(jsonobj)
			lim = int(content1["num"])

			if args == None:
				img = content1["img"]
				title = content1["title"]
				url = "https://xkcd.com"
			elif args.lower() in ["random", "rand"]:
				num = random.randint(1, lim+1)
				url = f"https://xkcd.com/{num}/info.0.json"
				async with self.bot.session.get(url) as req:
					obj = await req.text()
					status = req.status
				assert status == 200
				content = json.loads(obj)
				img = content["img"]
				title = content["title"]
				url = f"https://xkcd.com/{num}"
			elif args.isdigit():
				num = int(args)
				url = f"https://xkcd.com/{num}/info.0.json"
				async with self.bot.session.get(url) as req:
					status = req.status
					obj = await req.text()
				assert status == 200
				content = json.loads(obj)
				img = content["img"]
				title = content["title"]
				url = f"https://xkcd.com/{num}"
			else:
				img = content1["img"]
				title = content1["title"]
				url = "https://xkcd.com"

			embed = discord.Embed(title = title, url = url, color = 0x50C878, timestamp = datetime.datetime.now(datetime.timezone.utc))
			embed.set_image(url = img)
			embed.set_footer(text = "Visit xkcd.com for more comics!")
			await ctx.channel.send(embed = embed)
		except AssertionError:
			if req1.status != 200:
				raise discord.HTTPException(req1, "Comic not found!")
			else:
				raise discord.HTTPException(req, "Comic not found!")
		except:
			raise

	@commands.command()
	@commands.dm_only()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def confess(self, ctx, *, args):
		'''Sends anonymous messages to a specified channel on HoQ'''
		try:
			channel = self.bot.get_channel(849182001691885588)
			message = await channel.fetch_message(862718825463676938)
			num = int(message.content)
			msg = args
			channel = self.bot.get_channel(768129428793589782)
			embed = discord.Embed(description = msg, color = discord.Color.random(), timestamp = datetime.datetime.now(datetime.timezone.utc))
			embed.set_author(name = f"Anonymous Confession #{num}", icon_url = "https://media.discordapp.net/attachments/612249995290083348/617285079877681152/Sketch009.jpg")
			if ctx.message.attachments != []:
				url = ctx.message.attachments[0].url
				embed.set_image(url = url)
				if len(ctx.message.attachments) > 1:
					await ctx.channel.send("Can attach only one image!")
			embed.set_footer(text = "DM me with h!confess to confess on this channel!")
			await channel.send(embed = embed)
			await ctx.send("Sent!")
			num += 1
			await message.edit(content = num)
			await asyncio.sleep(5)
			c = self.bot.get_channel(864124566539599884)
			await c.send(f"{ctx.author.name}: {num-1}")
		except:
			raise

async def setup(bot):
	await bot.add_cog(Misc(bot))