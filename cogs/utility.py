import discord
import asyncio
import os
import typing
import json
import re
import datetime
from discord.ext import commands
from discord import app_commands
from utils.utils import ownercheck, isme
		
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
	async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
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
		await interaction.response.edit_message(embed = embed)
	
	@discord.ui.button(style = discord.ButtonStyle.success, label = "❯")
	async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
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
		await interaction.response.edit_message(embed = embed)
		
	@discord.ui.button(style = discord.ButtonStyle.success, label = "❯❯")
	async def jump(self, interaction: discord.Interaction, button: discord.ui.Button):
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
			await interaction.edit_original_message(embed=embed)
		else:
			await interaction.edit_original_message(content = "Invalid input provided")

	@discord.ui.button(style = discord.ButtonStyle.danger, label = "×")
	async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.edit_message(view = None)
		self.stop()

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.keys = [os.getenv(f"GoogleAPIKey{i}") for i in range(1,6)]
		self.cache = {}
		self.cache2 = {}

	group = app_commands.Group(name='search', description='Queries Google for media')

	async def _image(self, arg: str, gif: bool = False):
		query = arg.replace(" ", "-")
		if query in self.cache.keys() and gif == False:
			print('hit')
			return self.cache[query]
		elif query in self.cache2.keys() and gif == True:
			print('hit')
			return self.cache2[query]
		else:
			if gif == False:
				param = "&fileType=jpg-png"
			else:
				param = "&fileType=gif"
			queries = [f"https://www.googleapis.com/customsearch/v1?key={i}&cx=113278b73f24404b1&q={query}&searchType=image{param}&start={(self.keys.index(i)*10)+1}" for i in self.keys]
			images = []
			for q in queries:
				async with self.bot.session.get(q) as res:
					try:
						stat = res.status
						txt = await res.text()
						content = json.loads(txt)
						assert "items" in content.keys() and stat == 200
						for i in content["items"]:
							if i["fileFormat"] =="image/" and str(i['link']).count('url') != 1:
								images.append((i["title"], i["image"]["contextLink"], i["image"]["thumbnailLink"]))
							else:
								images.append((i["title"], i["image"]["contextLink"], i["link"]))
					except AssertionError:
						raise discord.HTTPException(response = res, message = content["error"]["message"])
					except:
						raise
			if not gif:
				self.cache.update({query: images})
			else:
				self.cache2.update({query: images})
			return images

	async def execute_image(self, user, search: str, gif: bool = False):
		resp = await self._image(search, gif)
		link = resp[0][2]
		if "(" in link and ")" in link:
			link = link.replace("(", "\(").replace(")", "\)")
		embed = discord.Embed(title = resp[0][0], url = resp[0][1], description = f"[Image URL]({link})", color = 0x00FF77, timestamp = datetime.datetime.now(datetime.timezone.utc))
		embed.set_image(url = resp[0][2])
		embed.set_author(name = user, icon_url = user.avatar.url)
		embed.set_footer(text = f"Page 1 of {len(resp)}")
		view = GoogleView(user = user, resp = resp, bot = self.bot)
		return (embed, view)
		

	@commands.command(aliases = ("im", "image"))
	async def img(self, ctx, *, search):
		'''Returns a list of fifty images using Google search'''
		embed, view = await self.execute_image(ctx.author, search)
		msg = await ctx.send(embed = embed, view = view)
		while True:
			result = await view.wait()
			if result:
				await msg.edit(view = None)
				break
			elif not result:
				break
	
	@commands.command()
	async def gif(self, ctx, *, search):
		'''Returns a list of fifty GIFs using Google search''' 
		embed, view = await self.execute_image(ctx.author, search, gif=True)
		msg = await ctx.send(embed = embed, view = view)
		while True:
			result = await view.wait()
			if result:
				await msg.edit(view = None)
				break
			elif not result:
				break

	@group.command(name = "image", description="Searches for static images")
	@app_commands.describe(search="Query string to search with")
	async def image(self, interaction: discord.Interaction, search: str):
		embed, view = await self.execute_image(interaction.user, search)
		await interaction.response.send_message(embed = embed, view = view)
		while True:
			result = await view.wait()
			if result:
				await interaction.response.edit_message(view = None)
				break
			elif not result:
				break

	@group.command(name = "gif", description="Searches for static images")
	@app_commands.describe(search="Query string to search with")
	async def GIF(self, interaction: discord.Interaction, search: str):
		embed, view = await self.execute_image(interaction.user, search, gif=True)
		await interaction.response.send_message(embed = embed, view = view)
		while True:
			result = await view.wait()
			if result:
				await interaction.response.edit_message(view = None)
				break
			elif not result:
				break

	@commands.command()
	@commands.check(isme)
	async def clear_cache(self, ctx):
		self.cache.clear()
		self.cache2.clear()
		await ctx.send('Cleared image caches!')
		
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
		if user.accent_color != None:
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
		if user.timed_out_until != None:
			embed.add_field(name='Timeout Expiration', value=user.timed_out_until.strftime("%d.%m.%Y, %H:%M:%S UTC"))
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
	@commands.guild_only()
	async def serverinfo(self, ctx: commands.Context):
		'''Returns information about the guild the command is used on'''
		name = ctx.author
		if ctx.author.avatar != None:
			userurl = ctx.author.avatar.url
		else:
			userurl = None
		roles, emojis, rolestr, emojistr, channelstr = [], [], None, None, None
		for i in ctx.guild.roles:
			roles.append(i.mention)
		roles.pop(0)
		if roles != []:
			rolestr = " ".join(roles)
		rcount = len(roles)
		for i in ctx.guild.emojis:
			if i.animated == True:
				emojis.append(f"<a:{i.name}:{i.id}>")
			else:
				emojis.append(f"<:{i.name}:{i.id}>")
		if emojis != []:
			emojistr = " ".join(emojis)
		ecount = len(emojis)
		ccount=len(ctx.guild.channels)
		channelstr = "\n".join([f"**{i.name}**: {len(i.channels)}" for i in ctx.guild.categories])
		channelstr += f"\n**No Category:** {len([i for i in ctx.guild.channels if i.category==None])}"

		embed = discord.Embed(color = 0x00FF99, timestamp = datetime.datetime.now(datetime.timezone.utc))
		embed.set_author(name = name, icon_url = userurl)
		if ctx.guild.icon is not None:
			embed.set_thumbnail(url = ctx.guild.icon.url)
		embed.add_field(name = "Name", value = f"{ctx.guild.name}", inline = True)
		embed.add_field(name = "Owner", value = f"{ctx.guild.owner}", inline = True)
		embed.add_field(name = "Created on", value = "{}".format(ctx.guild.created_at.strftime("%A, %B %d, %Y, %H:%M UTC")), inline = False)
		embed.add_field(name=f"Channel count[{ccount}]", value=channelstr)
		embed.add_field(name = "Preferred locale", value = f"{str(ctx.guild.preferred_locale).upper()}", inline = False)
		embed.add_field(name = "Verification level", value = f"{str(ctx.guild.verification_level).capitalize()}", inline = False)
		if rolestr == None or len(rolestr) < 1024:
			embed.add_field(name = f"Roles[{rcount}]", value = f"{rolestr}", inline = False)
		else:
			embed.add_field(name = f"Roles[{rcount}]", value = "Use `h!roles` for getting a list of roles", inline = False)
		if emojistr == None or len(emojistr) < 1024:
			embed.add_field(name = f"Emojis[{ecount}]", value = f"{emojistr}", inline = False)
		else:
			embed.add_field(name = f"Emojis[{ecount}]", value = "Use `h!emojilist` for getting a list of emojis on this server", inline = False)
		embed.set_footer(text = f"ID: {ctx.guild.id}")
		await ctx.channel.send(embed = embed)

	@commands.command()
	@commands.guild_only()
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

async def setup(bot):
	await bot.add_cog(Math(bot))
	await bot.add_cog(Utils(bot))
	await bot.add_cog(Info(bot))