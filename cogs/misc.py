from tkinter import E
import discord
import json
import random
import asyncio
import datetime

from discord import app_commands
from discord.ext import commands


def create_Embed(title: str, image_link: str, num: int):
	embed = discord.Embed(
			title = f"#{num} - {title}",
			url =  f'https://xkcd.com/{num}',
			color = 0x50C878,
			timestamp = datetime.datetime.now()
			)
	embed.set_image(url = image_link)
	embed.set_footer(text = "Visit xkcd.com for more comics!")

	return embed


async def parse_data(bot, num):
	async with bot.session.get(f'https://xkcd.com/{num}/info.0.json') as request:
		data = json.loads(await request.text())
	try:
		assert request.status == 200
	except AssertionError:
		raise discord.HTTPException(request, message = 'Could not fetch data from xkcd.com, please try again later!')
	except:
		raise
	else:
		return data


class xkcdView(discord.ui.View):
	def __init__(self, bot, count: int, max: int):
		super().__init__()
		self.bot = bot
		self.count: int = count
		self.max: int = max
		self._message: discord.Message = None

	@property
	def message(self) -> discord.Message:
		return self._message

	@message.setter
	def message(self, message: discord.Message) -> None:
		self._message = message

	@discord.ui.button(label="❮❮", style = discord.ButtonStyle.primary)
	async def oldest(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.count = 0
		data = await parse_data(self.bot, self.count)
		embed = create_Embed(data['title'], data['img'], self.count)
		await interaction.response.edit_message(embed = embed)

	@discord.ui.button(label="❮", style = discord.ButtonStyle.primary)
	async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.count == 1:
			self.count = self.max
		else:
			self.count -= 1
		data = await parse_data(self.bot, self.count)
		embed = create_Embed(data['title'], data['img'], self.count)
		await interaction.response.edit_message(embed = embed)

	@discord.ui.button(style = discord.ButtonStyle.primary, label = "Random")
	async def random(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.count = random.randint(1, self.max+1)
		data = await parse_data(self.bot, self.count)
		embed = create_Embed(data['title'], data['img'], self.count)
		await interaction.response.edit_message(embed = embed)

	@discord.ui.button(label='❯', style = discord.ButtonStyle.primary)
	async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.count == self.max:
			self.count = 1
		else:
			self.count += 1
		data = await parse_data(self.bot, self.count)
		embed = create_Embed(data['title'], data['img'], self.count)
		await interaction.response.edit_message(embed = embed)

	@discord.ui.button(label='❯❯', style = discord.ButtonStyle.primary)
	async def latest(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.count = self.max
		data = await parse_data(self.bot, self.count)
		embed = create_Embed(data['title'], data['img'], self.count)
		await interaction.response.edit_message(embed = embed)

	@discord.ui.button(label = '×', style = discord.ButtonStyle.danger)
	async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.stop()
		await interaction.response.edit_message(view = None)

	async def on_timeout(self) -> None:
		self.stop()
		await self.message.edit(view = None)

class Misc(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command()
	async def ping(self, ctx):
		ping = round(self.bot.latency*1000)
		await ctx.channel.send(f"Ping: {ping} ms")

	@app_commands.command(name='ping',description='Returns websocket latency (ping)')
	async def _ping(self, interaction: discord.Interaction):
		await interaction.response.send_message(f'Ping: {round(self.bot.latency*1000)} ms')
		
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
	async def xkcd(self, ctx, *, arg = ''):
		'''Shows an xkcd comic'''
		url1 = "https://xkcd.com/info.0.json"
		async with self.bot.session.get(url1) as req1:
			stat1 = req1.status
			data = json.loads(await req1.text())
		lim = int(data["num"])

		if stat1 != 200:
			raise discord.HTTPException(req1, 'Could not fetch information from xkcd.com, please try again later!')

		if arg.lower() == 'random':
			num = random.randint(1, lim+1)
			data = await parse_data(self.bot, num)

		elif arg.isdigit():
			num = int(arg)
			data = await parse_data(self.bot, num)

		embed = create_Embed(data['title'], data['img'], num)
		view = xkcdView(bot = self.bot, count = num, max = lim)
		view.message = await ctx.send(embed = embed, view = view)

	@commands.command()
	@commands.dm_only()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def confess(self, ctx, *, msg):
		'''Sends anonymous messages to a specified channel on HoQ'''
		try:
			channel = self.bot.get_channel(849182001691885588)
			message = await channel.fetch_message(862718825463676938)
			num = int(message.content)
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