import discord
import json
import datetime
from utils.utils import guildid, CancelButton

typedict = {True: "wildcard", False: "normal"}
nonepair = {"trigger": None, "response": None}

class SelectMenu(discord.ui.Select):
	def __init__(self, gid: int, wildcard: bool, user):
		opts = []
		self._user = user
		self.id = gid
		self._type = typedict[wildcard]
		with open("data/autoresponses.json") as fob:
			data = json.loads(fob.read())[str(self.id)][self._type]
			for i in data:
				opts.append(discord.SelectOption(label = i["trigger"]))
		
		super().__init__(placeholder = "Select an option", options = opts, row = 1)
		

	async def callback(self, interaction: discord.Interaction):
		if interaction.user != self._user:
			await interaction.response.send_message("You cannot use this select menu", ephemeral=True)
			return

		trigger = interaction.data["values"][0]
		with open("data/autoresponses.json") as fob:
			data = json.loads(fob.read())

		for i in data[str(self.id)][self._type]:
			if i["trigger"] == trigger:
				data[str(self.id)][self._type].remove(i)
				break
		if data[str(self.id)][self._type] == []:
			data[str(self.id)][self._type].append(nonepair)

		if nonepair in data[str(self.id)]["normal"] and nonepair in data[str(self.id)]["wildcard"]:
			data.pop(str(self.id))

		with open("data/autoresponses.json", "w") as fob:
			data = json.dump(data, fob, indent = 2)

		await interaction.response.send_message("Trigger removed!")
		for i in self.view.children:
			i.disabled = True
		self.placeholder = "This select menu has already been used"
		await interaction.message.edit(view = self.view)

class Slashcommands:
	'''Compiles all slashcommands in a single class'''
	
	def __init__(self, bot, interaction):
		self.bot = bot
		self.interaction: discord.Interaction = interaction
		self.data: dict = {}
		try:
			for i in self.interaction.data["options"]:
				self.data[i["name"]] = i["value"]
		except:
			pass

	async def execute(self):
		await getattr(self, self.interaction.data["name"])()

	async def ping(self):
		await self.interaction.response.send_message(f"Ping: {round(self.bot.latency*1000)} ms")

	async def addresponse(self):
		if any(["__" in self.data["response"], "lambda" in self.data["response"]]):
			await self.interaction.response.send_message("Cannot add that autoresponse!", ephemeral = True)
			return
			
		if not (self.interaction.user.guild_permissions.administrator or self.interaction.user.id == 586088176037265408):
			await self.interaction.response.send_message("You don't have the permission to use this command", ephemeral = True)
			return

		with open("data/autoresponses.json") as fob:
			data = json.loads(fob.read())
			
		id_ = guildid(self.interaction.guild_id)
		self.data["trigger"] = self.data["trigger"].lower()
		wildcard = self.data.pop("wildcard")
		type1, type2 = "normal", "wildcard"
		nonepair = {"trigger": None, "response": None}
		
		if wildcard:
			type1, type2 = type2, type1

		if str(id_) not in data:
			data[str(id_)] = {type1: [self.data], type2: [nonepair]}
		else:
			data[str(id_)][type1].append(self.data)
		
		if nonepair in data[str(id_)][type1] and len(data[str(id_)][type1]) > 1:
			data[str(id_)][type1].remove(nonepair)
		
		with open("data/autoresponses.json", "w") as fob:
			json.dump(data, fob, indent = 2)
		await self.interaction.response.send_message("Autoresponse successfully added!")

	async def removeresponse(self):
		if not (self.interaction.user.guild_permissions.administrator or self.interaction.user.id == 586088176037265408):
			await self.interaction.response.send_message("You don't have the permission to use this command!", ephemeral = True)
			return
			
		ID = guildid(self.interaction.guild_id)
		with open("data/autoresponses.json") as fob:
			data = json.loads(fob.read())

		if str(ID) not in data:
			await self.interaction.response.send_message("This guild does not have any trigger yet", ephemeral = True)
			return

		wildcard: bool = self.data.pop("wildcard")
		
		if nonepair in data[str(ID)][typedict[wildcard]]:
			await self.interaction.response.send_message("No trigger available under selected category", ephemeral =  True)
			return	
		
		view = discord.ui.View(timeout=60.0)
		view.add_item(SelectMenu(gid = ID, wildcard = wildcard, user = self.interaction.user))
		view.add_item(CancelButton(self.interaction.user))
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