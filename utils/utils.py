import discord
import datetime
from discord.ext import commands
from typing import Union

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
			embed = discord.Embed(description = self.list[self.count], timestamp = datetime.datetime.now(datetime.timezone.utc))
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

def admincheck(ctx: Union[commands.Context, discord.Interaction]) -> bool:
	if isinstance(ctx, commands.Context):
		if ctx.guild == None:
			raise commands.CheckFailure(message = "This command can be used on a guild only!")
		if not (ctx.author.guild_permissions.administrator or ctx.author.id == 586088176037265408 or ctx.guild.owner==ctx.author):
			raise commands.CheckFailure("You don't have the permission to use this command!")
	
	else:
		if ctx.guild == None:
			raise discord.app_commands.CheckFailure(message = "This command can be used on a guild only!")
		if not (ctx.user.guild_permissions.administrator or ctx.user.id == 586088176037265408 or ctx.guild.owner==ctx.user):
			raise discord.app_commands.CheckFailure("You don't have the permission to use this command!")
	return True

def moderatorcheck(ctx: Union[commands.Context, discord.Interaction]) -> bool:
	if isinstance(ctx, commands.Context):
		if ctx.guild == None:
			raise commands.CheckFailure(message = "This command can be used on a guild only!")
		if not (ctx.author.guild_permissions.manage_messages or ctx.author.id == 586088176037265408):
			raise commands.CheckFailure("You don't have the permission to use this command!")
	
	else:
		if ctx.guild == None:
			raise discord.app_commands.CheckFailure(message = "This command can be used on a guild only!")
		if not (ctx.user.guild_permissions.manage_messages or ctx.user.id == 586088176037265408):
			raise discord.app_commands.CheckFailure("You don't have the permission to use this command!")
	return True

def ownercheck(ctx: Union[commands.Context, discord.Interaction]) -> bool:
	if isinstance(ctx, commands.Context):
		user = ctx.author
	else:
		user = ctx.user
	return user.id == 586088176037265408

def guildid(id: int) -> int:
	if id in [850039242481991700,808257138882641960, 839939906558361627, 786520972064587786]:
		return 612234021388156938
	return id