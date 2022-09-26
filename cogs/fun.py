import datetime
import asyncio
import json
import random
import discord

from discord import app_commands
from discord.ext import commands



#helper classes and methods
def create_Embed(title: str, image_link: str, num: int) -> discord.Embed:
	embed = discord.Embed(
			title = f"#{num} - {title}",
			url =  f'https://xkcd.com/{num}',
			color = 0x50C878,
			timestamp = datetime.datetime.now()
			)
	embed.set_image(url = image_link)
	embed.set_footer(text = "Visit xkcd.com for more comics!")

	return embed


async def parse_data(bot, num) -> dict:
	try:
		async with bot.session.get(f'https://xkcd.com/{num}/info.0.json') as request:
			data = json.loads(await request.text())
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
		self.count = 1
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

	@discord.ui.button(label = '✕', style = discord.ButtonStyle.danger)
	async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.stop()
		await interaction.response.edit_message(view = None)

	async def on_timeout(self):
		self.stop()
		await self.message.edit(view = None)


class TTTButton(discord.ui.Button):
	def __init__(self, row, column):
		self.row = row
		self.column = column
		super().__init__(style = discord.ButtonStyle.primary, label = "\u200b \u200b \u200b", row = self.row)
	
	async def callback(self, interaction: discord.Interaction):
		view: TTTView = self.view
		state = view.board[self.column][self.row]
		if state in (1, -1):
			return
		
		if view.currentplayer == view.p2:
			view.currentplayer = view.p1
			view.board[self.column][self.row] = 1
			self.label = "X"
			self.style = discord.ButtonStyle.danger
			self.disabled = True
			content = f"{view.p1.mention}'s turn to play"
		elif view.currentplayer == view.p1:
			view.currentplayer = view.p2
			view.board[self.column][self.row] = -1
			self.label = "O"
			self.style = discord.ButtonStyle.success
			self.disabled = True
			content = f"{view.p2.mention}'s turn to play"

		winner = view.winner()
		if winner != None:
			if winner == view.p1:
				content = f"{view.p1.mention} won!"
			elif winner == view.p2:
				content = f"{view.p2.mention} won!"
			else:
				content = "It's a tie!"
			for child in view.children:
				child.disabled = True
			view.stop()
		await interaction.response.edit_message(content = content, view = view)


class TTTView(discord.ui.View):
	def __init__(self, p1: discord.Member, p2: discord.Member):
		super().__init__(timeout = 300.0)
		self.p1 = p1
		self.p2 = p2
		self.currentplayer = self.p2
		self.board = [
			[0, 0, 0],
			[0, 0, 0],
			[0, 0, 0]
			]
		
		for y in range(0, 3):
			for x in range(0, 3):
				self.add_item(TTTButton(row = y, column = x))

	async def interaction_check(self, interaction: discord.Interaction):
		if interaction.user not in (self.p1, self.p2):
			return False
		if interaction.user != self.currentplayer:
			await interaction.response.send_message("It's the other player's turn to play", ephemeral = True)
			return False
		return True
	
	async def on_timeout(self):
		self.stop()

	def winner(self):
		for across in self.board:
			if sum(across) == 3:
				return self.p2
			elif sum(across) == -3:
				return self.p1
			
		for line in range(3):
			val = self.board[0][line] + self.board[1][line] + self.board[2][line]
			if val == 3:
				return self.p2
			elif val == -3:
				return self.p1
		
		val = self.board[0][0] + self.board[1][1] + self.board[2][2]
		if val == 3:
			return self.p2
		elif val == -3:
			return self.p1

		val = self.board[0][2] + self.board[1][1] + self.board[2][0]
		if val == 3:
			return self.p2
		elif val == -3:
			return self.p1

		if all(i != 0 for row in self.board for i in row):
			return "Tie" 
		return None
#end of helper classes



class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases = ("ttt", "tictactoe", "tic-tac-toe"))
	async def TTT(self, ctx, p2: discord.Member):
		'''Creates a game of tic-tac-toe'''
		view = TTTView(p1 = ctx.author, p2 = p2)
		await ctx.send(content = f"Tic tac toe!\n{p2.mention}'s turn to play", view = view)
		await view.wait()

	@commands.command()
	async def hug(self, ctx, user: discord.Member = None):
		if user == None:
			string = f"*{ctx.author.mention} hugs themselves! ;-;*"
		else:
			string = f"*{ctx.author.mention} hugs {user.mention}!*"
		async with self.bot.session.get(r"https://some-random-api.ml/animu/hug") as request:
			try:
				assert int(request.status) == 200
				data: dict = json.loads(await request.text())
				assert "link" in data.keys()
			except AssertionError:
				raise discord.HTTPException("An error occurred!")
			except:
				raise
			else:
				url = data.get("link")
				embed = discord.Embed(color = 0x50C878, description = string)
				embed.set_image(url = url)
				embed.set_footer(text = "Credit for all GIFs goes to https://some-random-api.ml")
				await ctx.send(embed = embed)

	@commands.command()
	async def confetti(self, ctx):
		with open("/home/vcap/app/media/confetti.gif", "rb") as gif:
			return await ctx.send(file = discord.File(gif, filename = 'confetti.gif'))

	@commands.command()
	@commands.cooldown(1, 10, commands.BucketType.default)
	async def xkcd(self, ctx: commands.Context, *, arg: str = ''):
		'''Shows an xkcd comic'''
		url1 = "https://xkcd.com/info.0.json"
		async with self.bot.session.get(url1) as req1:
			stat1 = req1.status
			data = json.loads(await req1.text())
		lim = int(data["num"])

		if stat1 != 200:
			raise discord.HTTPException(req1, 'Could not fetch information from xkcd.com, please try again later!')

		if arg == '' or arg == 'latest':
			num = lim

		elif arg.lower() == 'random':
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
	async def confess(self, ctx: commands.Context, *, msg: discord.Message):
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
	await bot.add_cog(Fun(bot))