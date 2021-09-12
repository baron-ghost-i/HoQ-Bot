import discord
import datetime

class View(discord.ui.View):
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
	async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.count > 0:
			self.count -= 1
			embed = discord.Embed(description = self.list[self.count], timestamp = datetime.datetime.now(datetime.timezone.utc))
			embed.set_footer(text = f"Page {self.count+1} of {len(self.list)}")
			await interaction.message.edit(embed = embed)
		else:
			return
	
	@discord.ui.button(style = discord.ButtonStyle.success, label = "❯")
	async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
		if self.count < len(self.list)-1:
			self.count += 1
			embed = discord.Embed(description = self.list[self.count], timestamp = datetime.datetime.now(datetime.timezone.utc))
			embed.set_footer(text = f"Page {self.count+1} of {len(self.list)}")
			await interaction.message.edit(embed = embed)
		else:
			return
	
	@discord.ui.button(style = discord.ButtonStyle.danger, label = "×")
	async def end(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.stop()
		await interaction.message.edit(view = None)
