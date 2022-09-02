import re
import asyncio
import datetime
import enum
import discord

from discord import app_commands
from discord.ext import commands
from typing import Union
from utils import (
	PaginatorView,
	CancelButton,
	admincheck,
	guildid,
)

class SelectMenu(discord.ui.Select):
	def __init__(self, bot, gid: int, type: str, user):
		opts = []
		self.bot = bot
		self._user = user
		self.blankopt = discord.SelectOption(label = "None")
		self.id = gid
		data = [{'trigger': i['trigger'], 'response': i['response']} for i in self.bot.db['autoresponder'].find({'guild': gid, 'type': type})]
		for i in data:
			if type == 'reaction' or (i['response'].startswith('<') and i['response'].endswith(':>')):
				emoji = i['response']
			elif type == 'wildcard':
				emoji = '🇼'
			else:
				emoji = '🇳'
			print(emoji)
			opts.append(discord.SelectOption(label = i["trigger"], emoji = emoji))
		
		super().__init__(placeholder = "Select an option", options = opts)

	async def callback(self, interaction: discord.Interaction):
		if interaction.user != self._user:
			await interaction.response.send_message("You cannot use this select menu", ephemeral=True)
			return

		trigger = interaction.data["values"][0]

		self.bot.db['autoresponder'].find_one_and_delete({
			'guild': self.id,
			'trigger': trigger
		})

		await interaction.response.send_message("Trigger removed!")
		self.placeholder = "This select menu has already been used"
		for i in self.view.children:
			i.disabled = True
		self.view.stop()
		await interaction.message.edit(view = self.view)

class Autoresponder(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases = ('addresp',))
	@commands.guild_only()
	@commands.check(admincheck)
	async def addresponse(self, ctx: commands.Context, trigger, response: Union[discord.Emoji, str], type = "normal"):
		
		if isinstance(response, discord.Emoji):
			response = "<{}:{}:{}>".format(('a' if response.animated else ''), response.name, response.id)	
		if any(["__" in response, "lambda" in response]):
			return await ctx.send("Cannot add that autoresponse")
		if (not any([response.startswith('<:'), response.startswith('<a:')]) and re.sub('[.,;?!/\-\'\"]', '', response).isalnum()) and type == 'reaction':
			return await ctx.reply("Can't add a non-emoji response for reaction")

		id = guildid(ctx.guild.id)
		if self.bot.db['autoresponder'].find_one({'trigger': trigger, 'type': type, 'guild': id}) == None:
			self.bot.db['autoresponder'].insert_one({
				'guild': id,
				'trigger': trigger,
				'response': response,
				'type': type
			})
		else:
			self.bot.db['autoresponder'].find_one_and_update({'guild': id, 'type': type, 'trigger': trigger}, {'$set': {'response': response}})
		await ctx.send("Autoresponse successfully added")

	class Types(enum.Enum):
		normal = 'normal'
		wildcard = 'wildcard'
		reaction = 'reaction'

	@app_commands.command(name="addresponse", description="Adds a trigger-response pair to the autoresponder")
	@app_commands.describe(trigger='The trigger for the autoresponder', response='The response to the trigger', type='The type of the trigger(defaults to normal)')
	@app_commands.check(admincheck)
	async def _addresponse(self, interaction: discord.Interaction, trigger: str, response: str, type: Types = Types.normal):

		if any(["__" in response, "lambda" in response]):
			return await interaction.response.send_message("Cannot add that autoresponse!", ephemeral = True)
		if (not any([response.startswith('<:'), response.startswith('<a:')]) and re.sub('[.,;?!/\-\'\"]', '', response).isalnum()) and type.value == 'reaction':
			return await interaction.response.send_message("Can't add a non-emoji response for reaction", ephemeral = True)	
		if not interaction.user.guild_permissions.manage_messages:
			return await interaction.response.send_message("You do not have the permission to use this command", ephemeral = True)
			
		id_ = guildid(interaction.guild_id)

		if self.bot.db['autoresponder'].find_one({'trigger': trigger, 'type': type.value, 'guild': id_}) == None:
			self.bot.db['autoresponder'].insert_one({
				'guild': id_,
				'trigger': trigger,
				'response': response,
				'type': type.value
			})
		else:
			self.bot.db['autoresponder'].find_one_and_update({'guild': id_, 'type': type.value, 'trigger': trigger}, {'$set': {'response': response}})

		await interaction.response.send_message("Autoresponse successfully added!")
			
	@commands.command(aliases = ('removeresp',))
	@commands.guild_only()
	@commands.check(admincheck)
	async def removeresponse(self, ctx: commands.Context):
		if not (ctx.author.guild_permissions.administrator):
			await ctx.send("You do not have the permission to use this command!", delete_after = 5.0)
			return
			
		ID = guildid(ctx.guild_id)
		
		if self.bot.db['autoresponder'].count_documents({'guild': ID, 'type': type.value}) == 0:
			return await ctx.send("No trigger available under this category", delete_after = 5.0)	
		
		view = discord.ui.View(timeout=60.0)
		view.add_item(SelectMenu(bot = self.bot, gid = ID, type=type.value, user=ctx.author))
		view.add_item(CancelButton(user = ctx.author))
		await ctx.send("Select the autoresponse to remove", view = view)

	@app_commands.command(name='removeresponse', description='Removes a trigger-response pair from the autoresponder')
	@app_commands.describe(type='Select the type of reaction to be removed')
	@app_commands.check(admincheck)
	async def _removeresponse(self, interaction, type: Types):
		if not (interaction.user.guild_permissions.administrator):
			await interaction.response.send_message("You do not have the permission to use this command!", ephemeral = True)
			return
			
		ID = guildid(interaction.guild_id)
		
		if self.bot.db['autoresponder'].count_documents({'guild': ID, 'type': type.value}) == 0:
			return await interaction.response.send_message("No trigger available under this category", ephemeral =  True)	
		
		view = discord.ui.View(timeout=60.0)
		view.add_item(SelectMenu(bot = self.bot, gid = ID, type=type.value, user=interaction.user))
		view.add_item(CancelButton(user = interaction.user))
		await interaction.response.send_message("Select the autoresponse to remove", view = view)
			
	@commands.command(aliases = ('responses', 'resps'))
	@commands.guild_only()
	async def responselist(self, ctx):
		id = guildid(ctx.guild.id)
		if self.bot.db['autoresponder'].count_documents({"guild": id}) == 0:
			return await ctx.send("No autoresponse on this guild")

		wild = ""
		norm = ""
		react = ""
		for i in self.bot.db['autoresponder'].find({'guild': id}):
			if i['type'] == 'wildcard':
				wild += f"• `\"{i['trigger']}\"` — `\"{i['response']}\"`\n"
			elif i['type'] == 'reaction':
				react += f"• `\"{i['trigger']}\"` — `\"{i['response']}\"`\n"
			else:
				norm += f"• `\"{i['trigger']}\"` — `\"{i['response']}\"`\n"

		if wild == "":
			wild = "None"
		if norm == "":
			norm = "None"
		if react == "":
			react = "None"

		outstr = "__**Normal autoresponses:**__\n{} \n\n __**Wildcards:**__\n{} \n\n __**Reactions:**__\n {} ".format(norm, wild, react)

		if len(outstr) <= 4096:
			await ctx.send(embed = discord.Embed(description = outstr, color = 0x00FF77, timestamp = datetime.datetime.now()))
			return
			
		view = PaginatorView(input = outstr)
		embed = discord.Embed(description = view.list[0], timestamp = datetime.datetime.now())
		embed.set_footer(text = f"Page 1 of {len(view.list)}")
		await ctx.send(embed = embed, view = view)
		
				
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.guild == None:
			return
			
		id = guildid(message.guild.id)
		check = self.bot.db['Guild settings'].find_one({'_id': id})['autoresponder']
		
		if (not check) or message.author.bot:
			return
			
		dcheck = self.bot.db['Guild settings'].find_one({'_id': id})['dadmode']

		msg = re.sub('[.,;:?!/\-\'\"]', '', message.content).lower()

		normal = [(i['trigger'], i['response']) for i in self.bot.db['autoresponder'].find({'guild': id, 'type': 'normal'})]
		wild = [(i['trigger'], i['response']) for i in self.bot.db['autoresponder'].find({'guild': id, 'type': 'wildcard'})]
		react = [(i['trigger'], i['response']) for i in self.bot.db['autoresponder'].find({'guild': id, 'type': 'reaction'})]

		for i in react:
			if (msg.startswith(f"{i[0]} ")) or (msg.endswith(f" {i[0]}")) or (f" {i[0]} " in msg) or (msg == i[0]):
				try:
					await message.add_reaction(i[1])
				except:
					pass

		for i in normal:
			if msg == i[0].lower():
				async with message.channel.typing():
					await asyncio.sleep(0.5)
					try:
						reply = eval(i[1])
					except:
						reply = i[1]
					return await message.reply(reply)

		for i in wild:
			if (msg.startswith(f"{i[0]} ")) or (msg.endswith(f" {i[0]}")) or (f" {i[0]} " in msg) or (msg == i[0]):
				async with message.channel.typing():
					await asyncio.sleep(0.5)
					try:
						reply = eval(i[1])
					except:
						reply = i[1]
					return await message.reply(reply)

		if any([" i'm " in msg, " im " in msg, " i am " in msg, msg.startswith('im '), msg.startswith("i'm "), msg.startswith('i am ')]) and dcheck and len(msg) <= 2035:
			pos = None
			for i in ["im", "i am", "i'm"]:
				match = re.search(i, msg)
				if match != None:
					pos = match.end()
					break
			if pos != None:
				reply = f"Hi{msg[pos:]}, I'm dad!"
				async with message.channel.typing():
					await asyncio.sleep(0.5)
					return await message.reply(reply)
	
	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.guild.id == 612234021388156938:
			channel = self.bot.get_channel(612251604132823071)
			await channel.send(f'''Welcome to HoQ {member.mention}!
If you have a Quora account, make sure to send a link to it in this channel. If not, do let us know how you found us!
A moderator will verify you shortly, thank you for your patience and have a good time!''')

async def setup(bot):
	await bot.add_cog(Autoresponder(bot))