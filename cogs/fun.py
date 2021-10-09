import json
import discord
from discord.ext import commands

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
		if winner is not None:
			if winner == view.p1:
				content = f"{view.p1.mention} won!"
			elif winner == view.p2:
				content = f"{view.p2.mention} won!"
			else:
				content = "It's a tie!"
			for child in view.children:
				child.disabled = True
			view.stop()
		await interaction.message.edit(content = content, view = view)

class TTTView(discord.ui.View):
	def __init__(self, p1: discord.Member, p2: discord.Member):
		super().__init__(timeout = 300.0)
		self.p1 = p1
		self.p2 = p2
		self.currentplayer = self.p2
		self.board = [[0, 0, 0],
									[0, 0, 0],
									[0, 0, 0]]
		
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


	#I'll make it later
	'''@commands.command()
	async def hangman(self, ctx):
		await ctx.author.send("Type the phrase you want to use for the Hangman game. Make sure than the phrase is not more than 64 characters in length.")
		def qcheck(message):
			return len(message.content) <= 64 and message.type == discord.MessageType.private
		message = await self.bot.wait_for("message", check = qcheck)
		phrase = message.content
		len_ = len(phrase)'''

def setup(bot):
	bot.add_cog(Fun(bot))