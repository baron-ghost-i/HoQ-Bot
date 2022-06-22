import discord
import datetime

__all__ = [
	'PaginatorView',
	'CancelButton',
	'guildid',
	'to_discord_timestamp'
]

class PaginatorView(discord.ui.View):
	'''Creates a paginator for large embeds'''

	def __init__(self, input):
		super().__init__(timeout = None)
		self.input = input
		self.list = self.splitter()
		self.count = 0

	def splitter(self):
		resplist = []
		index1 = 0
		for i in range(len(self.input)//4096+1):
			if index1+4096 < len(self.input):
				index2 = self.input.rfind("\n", index1, 4096+index1)
				resplist.append(self.input[index1:index2])
				index1 = index2
			else:
				resplist.append(self.input[index1:])
		return resplist

	@discord.ui.button(style = discord.ButtonStyle.success, label = "❮")
	async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.count > 0:
			self.count -= 1
			embed = discord.Embed(description = self.list[self.count], timestamp = datetime.datetime.now())
			embed.set_footer(text = f"Page {self.count+1} of {len(self.list)}")
			await interaction.response.edit_message(embed = embed)
		else:
			return
	
	@discord.ui.button(style = discord.ButtonStyle.success, label = "❯")
	async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.count < len(self.list)-1:
			self.count += 1
			embed = discord.Embed(description = self.list[self.count], timestamp = datetime.datetime.now(datetime.timezone.utc))
			embed.set_footer(text = f"Page {self.count+1} of {len(self.list)}")
			await interaction.response.edit_message(embed = embed)
		else:
			return
	
	@discord.ui.button(style = discord.ButtonStyle.danger, label = "×")
	async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.stop()
		await interaction.response.edit_message(view = None)

class CancelButton(discord.ui.Button):
	'''Defines the working of a generic cancel button'''
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
		await interaction.response.edit_message(view = self.view)

def guildid(id: int) -> int:
	'''Mechanism for mapping guilds related to HoQ to HoQ, for synchronization'''
	if id in [850039242481991700,808257138882641960, 839939906558361627, 786520972064587786]:
		return 612234021388156938
	return id

def to_discord_timestamp(time: datetime.datetime) -> str:
	'''Returns a string which Discord interprets as a timestamp object'''
	return "<t:"+str(round(time.timestamp()))+">"