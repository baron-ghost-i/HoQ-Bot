import discord
import json
from utils.utils import guildid

class SelectMenu(discord.ui.Select):
	def __init__(self, gid: int, wildcard: bool, user):
		opts = []
		self._user = user
		self.blankopt = discord.SelectOption(label = "None")
		typedict = {True: "wildcard", False: "normal"}
		self.id = gid
		self.nonepair = {"trigger": None, "response": None}
		self._type = typedict[wildcard]
		with open("data/autoresponses.json") as fob:
			data = json.loads(fob.read())[str(self.id)][self._type]
			if self.nonepair in data:
				opts.append(self.blankopt)
			else:
				for i in data:
					opts.append(discord.SelectOption(label = i["trigger"]))
		
		super().__init__(placeholder = "Select an option", options = opts)

	async def callback(self, interaction: discord.Interaction):
		if self.blankopt in self.options:
			self.view.stop()
			return

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
			data[str(self.id)][self._type].append(self.nonepair)

		if self.nonepair in data[str(self.id)]["normal"] and self.nonepair in data[str(self.id)]["wildcard"]:
			data.pop(str(self.id))

		with open("data/autoresponses.json", "w") as fob:
			data = json.dump(data, fob, indent = 2)

		await interaction.response.send_message("Trigger removed!")
		self.view.stop()

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

	async def ping(self):
		await self.interaction.response.send_message(f"Ping: {round(self.bot.latency*1000)} ms")

	async def addresponse(self):
		if any(["__" in self.data["response"], "lambda" in self.data["response"]]):
			await self.interaction.response.send_message("Cannot add that autoresponse!", ephemeral = True)
			return
			
		if not self.interaction.user.guild_permissions.administrator:
			await self.interaction.response.send_message("You do not have the permission to use this command", ephemeral = True)
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
		if not self.interaction.user.guild_permissions.administrator:
			await self.interaction.response.send_message("You do not have the permission to use this command!", ephemeral = True)
			return
			
		ID = guildid(self.interaction.guild_id)
		with open("data/autoresponses.json") as fob:
			data = json.loads(fob.read())

		if str(ID) not in data:
			await self.interaction.response.send_message("This guild does not have any trigger yet", ephemeral =  True)
			return

		wildcard = self.data.pop("wildcard")
		view = discord.ui.View(timeout=60.0)
		view.add_item(SelectMenu(gid = ID, wildcard = wildcard))
		await self.interaction.response.send_message("Select the autoresponse to remove", view = view)