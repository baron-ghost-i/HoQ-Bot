import discord
from discord.ext import commands
from typing import Union
from utils.utils import guildid, admincheck

_dict = {True: "enabled", False: "disabled"}

class Configuration(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command = True)
	@admincheck()
	async def dadmode(self, ctx):
		state = self.bot.db["Guild settings"].find_one({"_id": guildid(ctx.guild.id)})["dadmode"]
		await ctx.send(f'''Dad mode is currently *{_dict[state]}*.
		More commands:
`h!autoresponder enable`: Enables dad mode
`h!autoresponder disable`: Disables dad mode''')
	
	@dadmode.command()
	async def enable(self, ctx):
		id = guildid(ctx.guild.id)
		self.bot.db["Guild settings"].update_one({"_id": id}, {"$set": {"dadmode": True}})
		await ctx.send("Enabled dad mode!")
	
	@dadmode.command()
	async def disable(self, ctx):
		id = guildid(ctx.guild.id)
		self.bot.db["Guild settings"].update_one({"_id": id}, {"$set": {"dadmode": False}})
		await ctx.send("Disabled dad mode!")

	@commands.group(invoke_without_command = True)
	@admincheck()
	async def autoresponder(self, ctx):
		state = self.bot.db["Guild settings"].find_one({"_id": guildid(ctx.guild.id)})["autoresponder"]
		await ctx.send(f'''Autoresponder is currently *{_dict[state]}*.
More commands:
`h!autoresponder enable`: Enables the autoresponder
`h!autoresponder disable`: Disables the autoresponder''')

	@autoresponder.command(aliases = ("enable",))
	async def _enable(self, ctx):
		id = guildid(ctx.guild.id)
		self.bot.db['Guild settings'].update_one({"_id": id}, {"$set": {"autoresponder": True}})
		await ctx.send("Autoresponder enabled!")

	@autoresponder.command(aliases = ("disable",))
	async def _disable(self, ctx):
		id = guildid(ctx.guild.id)
		self.bot.db['Guild settings'].update_one({"_id": id}, {"$set": {"autoresponder": False}})
		await ctx.send("Autoresponder disabled!")

	@commands.command()
	@admincheck()
	async def defaultrole(self, ctx, role: Union[discord.Role, int, str]):
		if ctx.channel.type == discord.ChannelType.private:
			pass
		id = guildid(ctx.guild.id)
		if isinstance(role, discord.Role):
			roleid = role.id
		elif isinstance(role, int):
			try:
				assert discord.utils.find(lambda r: r.id == role, ctx.guild.roles) != None
			except AssertionError:
				await ctx.send("Could not find the role!")
				return
			except:
				raise
			else:
				roleid = role
		else:
			try:
				role = discord.utils.find(lambda r: r.name == role, ctx.guild.roles)
				assert role != None
			except AssertionError:
				await ctx.send("Could not find the role!")
				return
			except:
				raise
			else:
				roleid = role.id
		self.bot.db["Guild settings"].update_one({"_id": id}, {"$set": {"default role": roleid}})
		await ctx.send("Default role set!")

def setup(bot):
	bot.add_cog(Configuration(bot))