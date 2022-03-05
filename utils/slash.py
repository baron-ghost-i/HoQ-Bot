import discord
import datetime
import re
from utils.utils import guildid

class CancelButton(discord.ui.Button):
	def __init__(self, user):
		self.user = user
		super().__init__(style = discord.ButtonStyle.danger, label = "Cancel", row = 2)
	
	async def callback(self, interaction: discord.Interaction):
		if interaction.user != self.user:
			return
		for i in self.view.children:
			i.disabled = True
			if isinstance(i, discord.ui.Select):
				i.placeholder = "Command cancelled"
		await interaction.message.edit(view = self.view)

class SelectMenu(discord.ui.Select):
	def __init__(self, bot, gid: int, type: str, user):
		opts = []
		self.bot = bot
		self._user = user
		self.blankopt = discord.SelectOption(label = "None")
		self.id = gid
		self._type = type
		data = [{'trigger': i['trigger'], 'response': i['response']} for i in self.bot.db['autoresponder'].find({'guild': gid, 'type': self._type})]
		
		for i in data:
			opts.append(discord.SelectOption(label = i["trigger"]))
		
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
		for i in self.view.children:
			i.disabled = True
		self.placeholder = "This select menu has already been used"
		await interaction.message.edit(view = self.view)
		self.view.stop()

		
class Slashcommands:
	def __init__(self, bot, interaction):
		self.bot = bot
		self.interaction: discord.Interaction = interaction
		self.data: dict = {}
		self.command = interaction.data.get('name')
		try:
			for i in self.interaction.data["options"]:
				self.data[i["name"]] = i["value"]
		except:
			pass

	async def execute(self):
		await getattr(self, self.command)()

	async def ping(self):
		await self.interaction.response.send_message(f"Ping: {round(self.bot.latency*1000)} ms")

	async def addresponse(self):
		if any(["__" in self.data["response"], "lambda" in self.data["response"]]):
			await self.interaction.response.send_message("Cannot add that autoresponse!", ephemeral = True)
			return

		if (not any([self.data['response'].startswith('<:'), self.data['response'].startswith('<a:')]) or re.sub('[.,;?!/\-\'\"]', '', self.data['response']).isalnum()) and self.data.get('type') == 'reaction':
			return await self.interaction.response.send_message("Can't add a non-emoji response for reaction", ephemeral = True)
			
		if not self.interaction.user.guild_permissions.manage_messages:
			await self.interaction.response.send_message("You do not have the permission to use this command", ephemeral = True)
			return
			
		id_ = guildid(self.interaction.guild_id)
		type = self.data.get("type", "normal")

		self.bot.db['autoresponder'].insert_one({
			'guild': id_,
			'trigger': self.data['trigger'],
			'response': self.data['response'],
			'type': type
		})

		await self.interaction.response.send_message("Autoresponse successfully added!")

	async def removeresponse(self):
		if not self.interaction.user.guild_permissions.administrator:
			await self.interaction.response.send_message("You do not have the permission to use this command!", ephemeral = True)
			return
			
		ID = guildid(self.interaction.guild_id)
		type = self.data['type']
		
		if self.bot.db['autoresponder'].count_documents({'guild': ID, 'type': type}) == 0:
			await self.interaction.response.send_message("No trigger available under this category", ephemeral =  True)
			return	
		
		view = discord.ui.View(timeout=60.0)
		view.add_item(SelectMenu(bot = self.bot, gid = ID, type = type, user=self.interaction.user))
		view.add_item(CancelButton(user = self.interaction.user))
		await self.interaction.response.send_message("Select the autoresponse to remove", view = view)

	async def mute(self):
		if not self.interaction.user.guild_permissions.moderate_members:
			await self.interaction.response.send_message('You do not have the permission to use this command', ephemeral = True)
			return

		member: discord.Member = discord.utils.find(lambda m: str(m.id) == self.data['member'], self.interaction.guild.members)
		if member.guild_permissions.administrator:
			await self.interaction.response.send_message('Cannot mute this member!', ephemeral = True)
			return
			
		reason = self.data.get('reason')
		d, h, m, s = self.data.get('days', 0), self.data.get('hours', 0), self.data.get('minutes', 0), self.data.get('seconds', 0)
		t = s+(60*m)+(60*60*h)+(24*60*60*d)
		
		if t > 2419200:
			await self.interaction.response.send_message("Timeout exceeds maximum time limit of 28 days", ephemeral = True)
			return

		if t == 0:
			timeout = None
		else:
			timeout = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()+t)

		await member.edit(timeout = timeout, reason = reason)
		await self.interaction.response.send_message("Member successfully {}! Reason: {}".format("muted" if timeout != None else "unmuted", reason))