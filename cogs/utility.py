import discord
import asyncio
import os
import typing
import json
import re
import datetime

from discord import app_commands
from discord.ext import commands
from utils import isme, ownercheck, to_discord_timestamp


_option_template = "• (**{}**) {} — **{}** votes"

_partition = '\n\n​**__Votes__**​\n\n'

def change_votes(data: list, embed: discord.Embed, count: int, vc: dict) -> discord.Embed:
	'''
# Parameters \n
* `data`:\n
	Data related to vote to be updated
* `embed`:\n
	Embed associated with poll message
* `count`:\n
	Number of votes
* `vc`:\n
	A dictionary containing the number of votes each candidate has
	'''

	#using docstring for the sake of sanity

	split = embed.description.split(_partition)
	cstr = split[1].split('\n')
	candidates = [i[0] for i in data]
	for entry in cstr:
		if int(entry[5]) in candidates:
			name = data[candidates.index(int(entry[5]))][1]
			cstr[cstr.index(entry)] = _option_template.format(entry[5], name, vc[int(entry[5])])

	message = split[0]+_partition+'\n'.join(cstr)

	embed2 = discord.Embed(
		description = message,
		color = embed.color,
		title = embed.title,
		timestamp = embed.timestamp
	)
	embed2.set_footer(text = embed.footer.text)

	return embed2


class Poll(discord.ui.View):

	def __init__(self, timeout: float, n: int, mv: int, opts: list):
		super().__init__(timeout = timeout)
		for i in range(1, n+1):
			button = PollButton(
				value = i,
				style = discord.ButtonStyle.primary,
				label = str(i)
				)
			self.add_item(button)
		self.add_item(ClearButton())
			
		self.max_v = mv
		self.choices = opts
		self.count: dict = {}
		for i in self.choices:
			self.count[i[0]] = 0

		self.pollresult = {}
		self.message: typing.Optional[discord.InteractionMessage] = None


class PollButton(discord.ui.Button):
	
	def __init__(self, value: int, *args, **kwargs):
		self.value = value
		super().__init__(*args, **kwargs)
		self.view: Poll

	async def callback(self, interaction: discord.Interaction):
		if interaction.user.id in self.view.pollresult and self.view.pollresult[interaction.user.id][0] == self.view.max_v:
			return await interaction.response.send_message('You have already voted! Please clear your votes to try again.', ephemeral = True)
		if interaction.user.id in self.view.pollresult:
			self.view.pollresult[interaction.user.id][0] += 1
			self.view.pollresult[interaction.user.id][1].append(self.value)
		else:
			self.view.pollresult[interaction.user.id] = [1, [self.value]]
		
		self.view.count[self.value] += 1
		data = []
		for i in self.view.pollresult[interaction.user.id][1]:
			for j in self.view.choices:
				if i == j[0]:
					data.append(j)
		embed = change_votes(data = data, embed = interaction.message.embeds[0], count = 1, vc = self.view.count)
		await interaction.message.edit(embed = embed)
		await interaction.response.send_message('Thank you for voting! Your vote has successfully been counted.', ephemeral = True)
			

class ClearButton(discord.ui.Button):
	def __init__(self):
		super().__init__(style = discord.ButtonStyle.danger, label = "✕ Clear Votes")
		self.view: Poll

	async def callback(self, interaction: discord.Interaction):
		if interaction.user.id not in self.view.pollresult:
			return await interaction.response.defer()

		data = []
		collector = self.view.pollresult.pop(interaction.user.id)[1]
		for i in collector:
			if self.view.count[i] > 0:
				self.view.count[i] -= 1
			for j in self.view.choices:
				if i == j[0]:
					data.append(j)

		embed = change_votes(data = data, embed = interaction.message.embeds[0], count = data[0], vc = self.view.count)
		await interaction.message.edit(embed = embed)
		await interaction.response.send_message('Your votes have been cleared!', ephemeral = True)

class Optionmaker(discord.ui.Modal):

	desc = discord.ui.TextInput(
		label = 'Description to be shown for the poll',
		style = discord.TextStyle.paragraph,
		placeholder = 'Enter description for the poll'
		)

	opts = discord.ui.TextInput(
                label = 'Choices (Enter each option in a new line)',
                style = discord.TextStyle.paragraph,
                placeholder = 'Poll choices'
                )
	
	def __init__(self, number: int, duration: float, mv: int, *args, **kwargs):
		self.n = number
		self.d = duration
		self.mv = mv
		super().__init__(*args, **kwargs)

	async def on_submit(self, interaction: discord.Interaction):
		l = self.opts.value.split('\n')
		if len(l) != self.n:
			return await interaction.response.send_message('Please provide as many choices as specified.', ephemeral = True)
		
		for i in l:
			setattr(self, f"Option{l.index(i)+1}", i)

		cstr = [_option_template.format(str(i), getattr(self, f'Option{i}'), '0') for i in range(1, self.n+1)]
		choices = [(i, getattr(self, f'Option{i}')) for i in range(1, (self.n + 1))]

		now = datetime.datetime.now()

		msg = self.desc.value +  f'\n\n **__Ends At__** \n\n <t:{round(now.timestamp()+self.d)}>' + _partition + '\n'.join(cstr)

		view = Poll(timeout = self.d, n = self.n, mv = self.mv, opts = choices)
		embed = discord.Embed(
			colour = 0x00FF77,
			title = 'POLL',
			description = msg,
			timestamp = now
		)

		await interaction.response.send_message(embed = embed, view = view)
		partial_message = await interaction.original_response()
		await asyncio.sleep(self.n)
		message = await partial_message.fetch()
		for i in view.children:
			i.disabled = True
		await message.edit(view = view)


class PageNo(discord.ui.Modal):

	page = discord.ui.TextInput(
		label='Which page would you like to go to?',
		style=discord.TextStyle.short,
		custom_id='pager',
		placeholder='Enter page number',
		min_length=1,
		max_length=2
		)

	def __init__(self, *args, **kwargs):
		self.pno: typing.Optional[int] = None
		super().__init__(*args, **kwargs)

	async def on_submit(self, interaction: discord.Interaction):
		if self.page.value.isdigit() and 1 <= int(self.page.value) <= 50:
			self.pno = int(self.page.value)
			await interaction.response.defer()
		else:
			await interaction.response.send_message('Invalid input! Please select a number between 1 and 50.', ephemeral=True)


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
		modal = PageNo(
			title='Jump to Page',
			timeout=30.0,
			custom_id='page_jumper'
			)

		await interaction.response.send_modal(modal)
		outcome = await modal.wait()
		
		if outcome or modal.pno is None:
			return await interaction.channel.send('Timed out!', delete_after=5.0)

		self.count = modal.pno - 1
		link = self.resp[self.count][2]
		if "(" in link and ")" in link:
			link = link.replace("(", "\(").replace(")", "\)")
		embed = discord.Embed(title = self.resp[self.count][0], url = self.resp[self.count][1], description = f"[Image URL]({link})", color = 0x00FF77, timestamp = datetime.datetime.now())
		embed.set_image(url = self.resp[self.count][2])
		embed.set_footer(text = f"Page {self.count+1} of {len(self.resp)}")
		embed.set_author(name = self.user, icon_url = self.user.avatar.url)
		await asyncio.sleep(0.25)
		await interaction.message.edit(embed=embed)

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
		if query in self.cache.keys() and not gif:
			print('hit')
			return self.cache[query]
		elif query in self.cache2.keys() and gif:
			print('hit')
			return self.cache2[query]
		else:
			if not gif:
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
							if i["fileFormat"] == "image/":
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
			link = link.replace("(", "%28").replace(")", "%29")
		embed = discord.Embed(title = resp[0][0], url = resp[0][1], description = f"[Image URL]({link})", color = 0x00FF77, timestamp = datetime.datetime.now(datetime.timezone.utc))
		embed.set_image(url = resp[0][2])
		embed.set_author(name = user, icon_url = user.avatar.url)
		embed.set_footer(text = f"Page 1 of {len(resp)}")
		view = GoogleView(user = user, resp = resp, bot = self.bot)
		return (embed, view)
		

	@commands.command(aliases = ("im", "image"))
	async def img(self, ctx: commands.Context, *, search):
		'''Returns a list of fifty images using Google search'''
		embed, view = await self.execute_image(ctx.author, search)
		msg = await ctx.send(embed = embed, view = view)
		result = await view.wait()
		if result:
			await msg.edit(view = None)
	
	@commands.command()
	async def gif(self, ctx: commands.Context, *, search):
		'''Returns a list of fifty GIFs using Google search''' 
		embed, view = await self.execute_image(ctx.author, search, gif=True)
		msg = await ctx.send(embed = embed, view = view)
		result = await view.wait()
		if result:
			await msg.edit(view = None)

	@group.command(name = "image", description="Searches for static images")
	@app_commands.describe(search="Query string to search with")
	async def image(self, interaction: discord.Interaction, search: str):
		embed, view = await self.execute_image(interaction.user, search)
		await interaction.response.send_message(embed = embed, view = view)
		result = await view.wait()
		if result:
			await interaction.edit_original_response(view = None)

	@group.command(name = "gif", description="Searches for static images")
	@app_commands.describe(search="Query string to search with")
	async def GIF(self, interaction: discord.Interaction, search: str):
		embed, view = await self.execute_image(interaction.user, search, gif=True)
		await interaction.response.send_message(embed = embed, view = view)
		result = await view.wait()
		if result:
			await interaction.edit_original_response(view = None)

	@commands.command()
	@commands.check(isme)
	async def clear_cache(self, ctx):
		self.cache.clear()
		self.cache2.clear()
		await ctx.send('Cleared image caches!')

	#to be recreated	
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

	@app_commands.command(name = 'poll', description = 'Creates a poll')
	@app_commands.describe(
		number = 'Number of choices to add to the poll (a maximum of 24 options can be added)',
		days = 'Duration (in days) for which the poll will accept votes.',
		hours = 'Duration (in hours) for which the poll will accept votes. Defaults to 24 hours (1 day).',
		max_votes = 'Maximum number of votes each member is allowed to cast. Default is 1'
		)
	async def _poll(self, interaction: discord.Interaction, number: int, days: float = 0.0, hours: float = 0.0, max_votes: int = 1):
		
		if number not in range(1, 25):
			return await interaction.response.send_message('Please provide a valid number of choices!', ephemeral=True)
		
		if days == 0 and hours == 0:
			return await interaction.response.send_message('Please provide a valid duration for the poll!', ephemeral=True)

		if max_votes < 1:
			return await interaction.response.send_message('Please provide a valid number for maximum votes allowed!', ephemeral = True)
		
		duration = round(days*24*60*60 + hours*60*60)

		modal = Optionmaker(number = number, duration = duration, title = 'New Poll', mv = max_votes)
		await interaction.response.send_modal(modal)


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
		regdate = to_discord_timestamp(user.created_at, rel = True, precise = True)
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
		timeout = False

		if isinstance(user, discord.Member):
			joindate = to_discord_timestamp(user.joined_at, rel = True, precise = True)
			rolelist = [i.mention for i in user.roles]
			rolelist.pop(0)
			rolelist.reverse()
			if rolelist != []:
				rolelength = len(rolelist)
				roles = ", ".join(rolelist)
			nick = user.nick
			timeout = user.is_timed_out()

		embed = discord.Embed(color = color, timestamp = datetime.datetime.now())
		embed.add_field(name = "ID", value = ID, inline = False)
		embed.add_field(name = "Username", value = name, inline = True)
		embed.add_field(name = "Nickname", value = nick, inline = True)
		embed.add_field(name = "Registered", value = regdate, inline = False)
		embed.add_field(name = "Joined", value = joindate, inline = False)
		embed.add_field(name = "Flags", value = flags, inline = False)
		embed.add_field(name = f"Roles [{rolelength}]", value = roles, inline = False)
		if timeout:
			embed.add_field(name='Timeout Expiration', value = to_discord_timestamp(user.timed_out_until, precise = True, rel = True))
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
		embed.add_field(name = "Created on", value = to_discord_timestamp(ctx.guild.created_at, rel = True), inline = False)
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