import discord
import asyncio
import os
import typing
import json
import re
import datetime
from discord.ext import commands
from utils.utils import ownercheck
		
class GoogleView(discord.ui.View):
	def __init__(self, bot, user: typing.Union[discord.Member, discord.User], resp: list, *, timeout: float = 90.0):
		super().__init__(timeout = timeout)
		self.bot = bot
		self.user = user
		self.count = 0
		self.resp = resp

	async def interaction_check(self, interaction):
		return interaction.user == self.user

	@discord.ui.button(style = discord.ButtonStyle.success, label = "❮")
	async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.count != 0:
			self.count -= 1
		else:
			self.count = 49 
		link = self.resp[self.count][2]
		if "(" in link and ")" in link:
			link = link.replace("(", "\(").replace(")", "\)")
		embed = discord.Embed(title = self.resp[self.count][0], url = self.resp[self.count][1], description = f"[Image URL]({link})", color = 0x00FF77, timestamp = datetime.datetime.now())
		embed.set_image(url = self.resp[self.count][2])
		embed.set_footer(text = f"Page {self.count+1} of {len(self.resp)}")
		embed.set_author(name = self.user, icon_url = self.user.avatar.url)
		await asyncio.sleep(0.25)
		await interaction.message.edit(embed = embed)
	
	@discord.ui.button(style = discord.ButtonStyle.success, label = "❯")
	async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.count != 49:
			self.count += 1
		else:
			self.count = 0 
		link = self.resp[self.count][2]
		if "(" in link and ")" in link:
			link = link.replace("(", "\(").replace(")", "\)")
		embed = discord.Embed(title = self.resp[self.count][0], url = self.resp[self.count][1], description = f"[Image URL]({link})", color = 0x00FF77, timestamp = datetime.datetime.now())
		embed.set_image(url = self.resp[self.count][2])
		embed.set_footer(text = f"Page {self.count+1} of {len(self.resp)}")
		embed.set_author(name = self.user, icon_url = self.user.avatar.url)
		await asyncio.sleep(0.25)
		await interaction.message.edit(embed = embed)
		
	@discord.ui.button(style = discord.ButtonStyle.success, label = "❯❯")
	async def jump(self, button: discord.ui.Button, interaction: discord.Interaction):
		def check(message):
			return message.content.isdigit() == True and 0 <= int(message.content) <= 50 and message.author == self.user
		await interaction.response.send_message(content = "Which page would you like to go to?")
		msg = await self.bot.wait_for("message", check = check)
		if msg is not None:
			self.count = int(msg.content)-1
			link = self.resp[self.count][2]
			if "(" in link and ")" in link:
				link = link.replace("(", "\(").replace(")", "\)")
			embed = discord.Embed(title = self.resp[self.count][0], url = self.resp[self.count][1], description = f"[Image URL]({link})", color = 0x00FF77, timestamp = datetime.datetime.now())
			embed.set_image(url = self.resp[self.count][2])
			embed.set_footer(text = f"Page {self.count+1} of {len(self.resp)}")
			embed.set_author(name = self.user, icon_url = self.user.avatar.url)
			await asyncio.sleep(0.25)
			await interaction.message.edit(embed = embed)
		else:
			await interaction.response.send_message(content = "Invalid input provided")

	@discord.ui.button(style = discord.ButtonStyle.danger, label = "×")
	async def end(self, button: discord.ui.Button, interaction: discord.Interaction):
		await interaction.message.edit(view = None)
		self.stop()

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.key1 = os.getenv("GoogleAPIKey1")
		self.key2 = os.getenv("GoogleAPIKey2")
		self.key3 = os.getenv("GoogleAPIKey3")
		self.key4 = os.getenv("GoogleAPIKey4")
		self.key5 = os.getenv("GoogleAPIKey5")
		self.cache = {}
		self.cache2 = {}

	async def image(self, arg, gif: bool = False):
		query = "-".join(list(arg)).lower()
		if query in self.cache.keys():
			print("cache hit!")
			return self.cache[f"{query}"]
		else:
			if gif == False:
				param = ""
			else:
				param = "&fileType=gif"
			q1, q2, q3, q4, q5 = f"https://www.googleapis.com/customsearch/v1?key={self.key1}&cx=113278b73f24404b1&q={query}&searchType=image{param}", f"https://www.googleapis.com/customsearch/v1?key={self.key2}&cx=113278b73f24404b1&q={query}&searchType=image&{param}&start=11", f"https://www.googleapis.com/customsearch/v1?key={self.key3}&cx=113278b73f24404b1&q={query}&searchType=image{param}&start=21", f"https://www.googleapis.com/customsearch/v1?key={self.key4}&cx=113278b73f24404b1&q={query}&searchType=image{param}&start=31", f"https://www.googleapis.com/customsearch/v1?key={self.key5}&cx=113278b73f24404b1&q={query}&searchType=image{param}&start=41"
			lis = []
			for q in [q1, q2, q3, q4, q5]:
				async with self.bot.session.get(q) as res:
					try:
						stat = res.status
						txt = await res.text()
						content = json.loads(txt)
						assert "items" in content.keys() and stat == 200
						for i in content["items"]:
							if i["fileFormat"] =="image/":
								lis.append((i["title"], i["image"]["contextLink"], i["image"]["thumbnailLink"]))
							else:
								lis.append((i["title"], i["image"]["contextLink"], i["link"]))
					except AssertionError:
						raise discord.HTTPException(response = res, message = content["error"]["message"])
						break
					except:
						raise
						break
			self.cache.update({f"{query}": lis})
			return lis

	@commands.command(aliases = ("im", "image"))
	async def img(self, ctx, *args):
		'''Returns a list of fifty images using Google search'''
		resp = await self.image(args)
		link = resp[0][2]
		if "(" in link and ")" in link:
			link = link.replace("(", "\(").replace(")", "\)")
		embed = discord.Embed(title = resp[0][0], url = resp[0][1], description = f"[Image URL]({link})", color = 0x00FF77, timestamp = datetime.datetime.now(datetime.timezone.utc))
		embed.set_image(url = resp[0][2])
		embed.set_author(name = ctx.author, icon_url = ctx.author.avatar.url)
		embed.set_footer(text = f"Page 1 of {len(resp)}")
		view = GoogleView(user = ctx.author, resp = resp, bot = self.bot)
		msg = await ctx.send(embed = embed, view = view)
		while True:
			result = await view.wait()
			if result:
				await msg.edit(view = None)
				break
			elif not result:
				break
	
	@commands.command()
	async def gif(self, ctx, *args):
		'''Returns a list of fifty GIFs using Google search''' 
		resp = await self.image(args, gif = True)
		link = resp[0][2]
		if "(" in link and ")" in link:
			link = link.replace("(", "\(").replace(")", "\)")
		embed = discord.Embed(title = resp[0][0], url = resp[0][1], description = f"[Image URL]({link})", color = 0x00FF77, timestamp = datetime.datetime.now(datetime.timezone.utc))
		embed.set_image(url = resp[0][2])
		embed.set_footer(text = f"Page 1 of {len(resp)}")
		view = GoogleView(user = ctx.author, resp = resp, bot = self.bot)
		msg = await ctx.send(embed = embed, view = view)
		while True:
			result = await view.wait()
			if result:
				await msg.edit(view = None)
				break
			elif not result:
				break
		
	@commands.command()
	async def poll(self, ctx, *args):
		'''Creates a poll'''
		emoji = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣", "🔟"]
		args = list(args)
		if len(args) == 0:
			pass
		elif len(args) == 1:
			q = args.pop(0)
			options = ["Yes", "No"]
		elif len(args) > 11:
			return
		else:
			q = args.pop(0)
			options = [i for i in args]
			
		try:
			lis = []
			for i in range(len(options)):
				lis.append("{} {}".format(emoji[i], options[i]))
			optionstr = "\n".join(lis)
			pollbody = f"{q}\n{optionstr}"
			
			embed = discord.Embed(title = "Poll!", description = pollbody, color = 0xFfD700, timestamp = datetime.datetime.now(datetime.timezone.utc))
			msg = await ctx.channel.send(embed = embed)
			await ctx.message.delete()
			for i in range(len(options)):
				await msg.add_reaction(emoji[i])
		except:
			raise

class Math(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command = True)
	async def math(self, ctx):
		await ctx.channel.send(embed = discord.Embed(description = '''Proper usage:
`h!math convert`: Converts characters with foreslash to respective math symbols
`h!math list`: Retuns the available list of symbols and their names
`h!math create`: Adds a new symbol for the bot to access													 
		''', color = 0x1DACD6, timestamp = datetime.datetime.now(datetime.timezone.utc)))

	@math.command()
	async def convert(self, ctx, *, input):
		'''Converts all possible mathematical symbol names into Unicode-supported symbols'''
		args = re.split(r"\s|\\", input)
		for i in args:
			symbol = self.bot.db['Math'].find_one({'name': i})
			if symbol != None:
				args[args.index(i)] = symbol['symbol']
			else:
				pass
		for i in args:
			if i == "":
				args.pop(args.index(i))
		rep = "".join(args)
		await ctx.channel.send(rep)

	@math.command(aliases = ("list",))
	async def show(self, ctx):
		'''Returns a list of convertible symbols available'''
		l = []
		for i in self.bot.db['Math'].find():
			l.append(f"\\{i['name']}: {i['symbol']}")
		resp = "\n".join(l)
		await ctx.channel.send(embed = discord.Embed(title = "List of available symbols", description = resp, color = 0x00FF99, timestamp = datetime.datetime.now(datetime.timezone.utc)))

	@math.command(aliases = ('add',))
	@commands.check(ownercheck)
	async def create(self, ctx, name, symbol):
		'''Adds a new symbol to the list of available symbols'''
		try:
			self.bot.db['Math'].insert_one({'name': name, 'symbol': symbol})
			await ctx.send('Symbol added successfully')
		except:
			raise

class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(aliases = ("av", "pfp"))
	async def avatar(self, ctx, *, args: discord.User = None):
		'''Returns the avatar for a user'''
		embed = discord.Embed(color = discord.Color.random(), timestamp = datetime.datetime.now(datetime.timezone.utc))
		if args == None:
			name, url = ctx.author, ctx.author.avatar.url
		else:
			name, url = args, args.avatar.url
		embed.set_author(name = f"{name}", icon_url = url)
		embed.set_image(url = f"{url}")
		embed.set_footer(text = f"Requested by {ctx.author}")
		await ctx.channel.send(embed = embed)

	@commands.command(aliases = ("whois",))
	async def userinfo(self, ctx, user: typing.Union[discord.Member, discord.User, int] = None):
		'''Returns information about a specified member'''
		if user == None:
			user = ctx.author
		if isinstance(user, int):
			try:
				user = await self.bot.fetch_user(user)
			except:
				raise commands.UserNotFound("Couldn't find any user!")
		
		name = f"{user.name}#{user.discriminator}"
		regdate = user.created_at.strftime("%A, %B %d, %Y, %H:%M UTC")
		ID = user.id
		flags = user.public_flags.all()
		if user.bot:
			flags.append("Bot")
		if flags != []:
			flags = ", ".join([str(i).replace("UserFlags.", "").replace("_", " ").title() for i in flags])
		else:
			flags = None
		if user.accent_color is not None:
			color = user.accent_color
		else:
			color = discord.Color.teal()
		roles = None
		rolelength = 0
		joindate = None
		nick = None

		if isinstance(user, discord.Member):
			joindate = user.joined_at.strftime("%A, %B %d, %Y, %H:%M UTC")
			rolelist = [i.mention for i in user.roles]
			rolelist.pop(0)
			rolelist.reverse()
			if rolelist != []:
				rolelength = len(rolelist)
				roles = ", ".join(rolelist)
			nick = user.nick

		embed = discord.Embed(color = color, timestamp = datetime.datetime.now())
		embed.add_field(name = "ID", value = ID, inline = False)
		embed.add_field(name = "Username", value = name, inline = True)
		embed.add_field(name = "Nickname", value = nick, inline = True)
		embed.add_field(name = "Registered", value = regdate, inline = False)
		embed.add_field(name = "Joined", value = joindate, inline = False)
		embed.add_field(name = "Flags", value = flags, inline = False)
		embed.add_field(name = f"Roles [{rolelength}]", value = roles, inline = False)
		if user.avatar != None:
			embed.set_thumbnail(url = user.avatar.url)
			embed.set_author(name = user, icon_url = user.avatar.url)
		else:
			embed.set_author(name = user)
		embed.set_footer(text = f"Requested by {ctx.author}")
		if user.banner:
			embed.set_image(url = user.banner.url)
		async with ctx.typing():
			await asyncio.sleep(1)
		await ctx.send(embed = embed)

	@commands.command()
	async def serverinfo(self, ctx):
		'''Returns information about the guild the command is used on'''
		name = ctx.author
		if ctx.author.avatar != None:
			userurl = ctx.author.avatar.url
		else:
			userurl = discord.Embed.Empty
		roles, rolestr, emojis, emojistr = [], None, [], None
		for i in ctx.guild.roles:
			roles.append(i.mention)
		roles.pop(0)
		if roles != []:
			rolestr = " ".join(roles)
		num1 = len(roles)
		for i in ctx.guild.emojis:
			if i.animated == True:
				emojis.append(f"<a:{i.name}:{i.id}>")
			else:
				emojis.append(f"<:{i.name}:{i.id}>")
		if emojis != []:
			emojistr = " ".join(emojis)
		num2 = len(emojis)

		embed = discord.Embed(color = 0x00FF99, timestamp = datetime.datetime.now(datetime.timezone.utc))
		embed.set_author(name = name, icon_url = userurl)
		if ctx.guild.icon is not None:
			embed.set_thumbnail(url = ctx.guild.icon.url)
		embed.add_field(name = "Name", value = f"{ctx.guild.name}", inline = True)
		embed.add_field(name = "Owner", value = f"{ctx.guild.owner}", inline = True)
		embed.add_field(name = "Created on", value = "{}".format(ctx.guild.created_at.strftime("%A, %B %d, %Y, %H:%M UTC")), inline = False)
		embed.add_field(name = "Region", value = f"{str(ctx.guild.region).capitalize()}", inline = False)
		embed.add_field(name = "Verification level", value = f"{str(ctx.guild.verification_level).capitalize()}", inline = False)
		if rolestr == None or len(rolestr) < 1024:
			embed.add_field(name = f"Roles[{num1}]", value = f"{rolestr}", inline = False)
		else:
			embed.add_field(name = f"Roles[{num1}]", value = "Use `h!roles` for getting a list of roles", inline = False)
		if emojistr == None or len(emojistr) < 1024:
			embed.add_field(name = f"Emojis[{num2}]", value = f"{emojistr}", inline = False)
		else:
			embed.add_field(name = f"Emojis[{num2}]", value = "Use `h!emojilist` for getting a list of emojis on this server", inline = False)
		embed.set_footer(text = f"ID: {ctx.guild.id}")
		await ctx.channel.send(embed = embed)

	@commands.command()
	async def roles(self, ctx):
		'''Returns a list of roles'''
		l = []
		for i in ctx.guild.roles:
			l.append(i.mention)
		l.pop(0)
		l.reverse()
		if len(l) != 0:
			roles = "\n".join(l)
		else:
			roles = None
		await ctx.channel.send(embed = discord.Embed(title = "Roles", description = f"{roles}", color = 0x00FF99))

	@commands.command()
	async def servericon(self, ctx):
		'''Returns the server icon'''
		embed = discord.Embed(color = 0x00FF99, timestamp = datetime.datetime.now(datetime.timezone.utc))
		embed.set_image(url = ctx.guild.icon.url)
		await ctx.channel.send(embed = embed)

def setup(bot):
	bot.add_cog(Math(bot))
	bot.add_cog(Utils(bot))
	bot.add_cog(Info(bot))