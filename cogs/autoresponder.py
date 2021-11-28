import discord
import json
import asyncio
import re
import datetime
from discord.ext import commands
from utils import paginatorview

class Autoresponder(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.nonepair = {"trigger": None, "response": None}

	def id(self, id: int):
		if any([id == 850039242481991700, id == 808257138882641960, id == 839939906558361627, id == 786520972064587786]):
			return 612234021388156938
		return id
	
	def ownercheck():
		async def predicate(ctx):
			if ctx.guild is None:
				raise commands.CheckFailure(message = "This command can be used on a guild only!")
				return False
			if not (ctx.author.guild_permissions.administrator or ctx.author.id == 586088176037265408):
				raise commands.CheckFailure("You don't have the permission to use this command!")
				return False
			return True
		return commands.check(predicate)

	@commands.Cog.listener()
	async def on_message(self, ctx: discord.Message):
		if ctx.channel.type == discord.ChannelType.private:
			return
			
		id = self.id(ctx.guild.id)
		flag1, flag2, message = False, False, ctx.content
		with open("data/autoresponses.json", "r") as foo:
			content = json.loads(foo.read())
		
		if ctx.guild == None or str(id) not in content.keys():
			return
		
		if ctx.author.bot:
			return

		nonwildkeys, nonwildresp = [i["trigger"] for i in content[f"{id}"]["normal"]], [i["response"] for i in content[f"{id}"]["normal"]]

		wildkeys, wildresp = [i["trigger"] for i in content[f"{id}"]["wildcard"]], [i["response"] for i in content[f"{id}"]["wildcard"]]

		if any([message.lower() == "oop-", message.lower().startswith("oop- "), message.lower().endswith("oop-"), " oop- " in message.lower()]):
			await ctx.add_reaction("<:eyez:684985729780154370>")
			return

		if message.lower() in nonwildkeys:
			try:
				reply = eval(nonwildresp[nonwildkeys.index(message.lower())])
			except:
				reply = nonwildresp[nonwildkeys.index(message.lower())]
			async with ctx.channel.typing():
				await asyncio.sleep(1)
			await ctx.reply(reply)
			return
		
		for i in wildkeys:
			if any ([message.lower().startswith(f"{i} "), message.lower().endswith(f" {i}"), message.lower().endswith(f" {i}."), f" {i} " in message.lower(), i == message.lower()]):
				flag1, index = True, wildkeys.index(i)
				break
		
		if flag1 == True:
			try:
				reply = eval(wildresp[index])
			except:
				reply = wildresp[index]
			async with ctx.channel.typing():
				await asyncio.sleep(1)
			await ctx.reply(reply)
			flag1 = False
			return
		
		if len(message.lower()) <= 2035:
			if any([message.lower().startswith("i\'m "), message.lower().startswith("im "), message.lower().startswith("i am ")]):
				for i in ["im ", "i am ", "i\'m "]:
					match = re.search(i, message.lower())
					if match is not None:
						pos = match.end()
						flag2 = True
						break
			
			elif any([" im " in message.lower(), " i am " in message.lower(), " i'm " in message.lower()]):
				for i in [" im ", " i am ", " i\'m "]:
					match = re.search(i, message.lower())
					if match is not None:
						pos = match.end()
						flag2 = True
						break
		
		if flag2 == True:
			reply = f"Hi {message[pos:]}, I'm dad!"
			await ctx.reply(reply)
			flag2 = False
			return

	@commands.command(aliases = ("addresp",))
	@ownercheck()
	async def addresponse(self, ctx: commands.Context, trigger, response, wildcard: str = None):
		trigger = trigger.lower()
		if any(["__" in response, "lambda" in response]):
			await ctx.send("Cannot add that autoresponse")
			return

		id = self.id(ctx.guild.id)
		if wildcard == None or wildcard.lower() != "wildcard":
			ctype, ctype2 = "normal", "wildcard"
		else:
			ctype, ctype2 = "wildcard", "normal"
		pair = {"trigger": trigger, "response": response}
		with open("data/autoresponses.json", "r") as foo:
			content = json.loads(foo.read())
		try:
			assert str(id) in content.keys()
		except AssertionError:
			content.update({f"{id}": {ctype: [pair], ctype2: [self.nonepair]}})
		else:
			content[str(id)][ctype].append(pair)
			for i in content[str(id)][ctype]:
				if i == self.nonepair:
					content[str(id)][ctype].remove(i)
		with open("data/autoresponses.json", "w") as foo:
			foo.write(json.dumps(content, indent = 2))
		await asyncio.sleep(0.5)
		await ctx.send("Added response!")

	@commands.command(aliases = ("removeresp",))
	@ownercheck()
	async def removeresponse(self, ctx: commands.Context, *, trigger: str):
		id = self.id(ctx.guild.id)
		with open("data/autoresponses.json", "r") as foo:
			content = json.loads(foo.read())
		try:
			assert str(id) in content.keys()
		except AssertionError:
			await ctx.send("This guild does not have any autoresponse!")
			return
		except:
			raise
		else:
			ctype, ctype2 = "normal", "wildcard"
			normlist, wildlist = [i["trigger"] for i in content[str(id)][ctype]], [i["trigger"] for i in content[str(id)][ctype2]]
			try:
				assert trigger in normlist+wildlist
			except AssertionError:
				await ctx.send("No such autoresponse found!")
				return
			except:
				raise
			else:
				if trigger in normlist:
					content[str(id)][ctype].pop(normlist.index(trigger))
				else:
					content[str(id)][ctype2].pop(wildlist.index(trigger))
					
				if content[str(id)][ctype] != [] and content[str(id)][ctype2] == []:
					content[str(id)][ctype2].append(self.nonepair)
				
				elif content[str(id)][ctype] == [] and content[str(id)][ctype2] != []:
					content[str(id)][ctype].append(self.nonepair)
				
				if content[str(id)][ctype] == content[str(id)][ctype2] == [self.nonepair]:
					content.pop(str(id))
				
		with open("data/autoresponses.json", "w") as foo:
					foo.write(json.dumps(content, indent = 2))
		await asyncio.sleep(0.5)
		await ctx.send("Removed response!")
				
	@commands.command(aliases = ("responses", "resps", "autoresps"))
	@commands.guild_only()
	async def autoresponses(self, ctx: commands.Context):
		id = self.id(ctx.guild.id)
		with open("data/autoresponses.json", "r") as foo:
			content = json.loads(foo.read())
		try:
			assert str(id) in content.keys()
		except AssertionError:
			await ctx.send("No autoresponse for this guild! Try using `h!addresponse` to create a new response")
		else:
			nonwild = ["• `\"{}\"` — `\"{}\"`".format(i["trigger"], i["response"]) for i in content[str(id)]["normal"]]
			wild = ["• `\"{}\"` — `\"{}\"`".format(i["trigger"], i["response"]) for i in content[str(id)]["wildcard"]]
			normresp = "__**Normal autoresponses:**__\n"+"\n".join(nonwild)
			wildresp = "__**Wildcards:**__\n"+"\n".join(wild)
			response = normresp + "\n\n" + wildresp
			response = response.replace("`\"None\"` — `\"None\"`", "None")
			try:
				assert len(response) <= 4096
			except AssertionError:
				view = paginatorview.View(input = response)
				embed = discord.Embed(description = view.list[0], timestamp = datetime.datetime.now())
				embed.set_footer(text = f"Page 1 of {len(view.list)}")
				await ctx.send(embed = embed, view = view)
			else:
				await ctx.send(embed = discord.Embed(description = response, color = 0x00FF77, timestamp = datetime.datetime.now()))
	
	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.guild.id == 612234021388156938:
			channel = self.bot.get_channel(612251604132823071)
			await asyncio.sleep(0.5)
			await channel.send(f'''Welcome to HoQ {member.mention}! To get verified, post a link to your Quora account. If you do not have a Quora account, let us know how you found the server.
Thank you for your patience! A moderator will verify you shortly.''')

def setup(bot):
	bot.add_cog(Autoresponder(bot))