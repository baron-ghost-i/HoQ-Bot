import discord
from discord.ext import commands
from typing import Union

class Configuration(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command = True)
	async def dadmode(self, ctx):
		await ctx.send('''Correct usage:
		`h!dadmode enable`: Enables dad mode \(warning: can be frustrating\)
		`h!dadmode disable`: Disables dad mode''')
	
	@dadmode.command()
	async def enable(self, ctx):
		self.bot.db["Guild settings"].update_one({"_id": ctx.guild.id}, {"$set": {"dadmode": True}})
		await ctx.send("Enabled dad mode!")
	
	@dadmode.command()
	async def disable(self, ctx):
		self.bot.db["Guild settings"].update_one({"_id": ctx.guild.id}, {"$set": {"dadmode": False}})
		await ctx.send("Disabled dad mode!")

	@commands.group(invoke_without_command = True)
	async def defaultrole(self, ctx, role: Union[discord.Role, int, str]):
		if isinstance(role, discord.Role):
			roleid = role.id
		elif isinstance(role, int):
			try:
				role = discord.utils.find(lambda r: r.name == role, ctx.guild.roles)
				assert role != None
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
		self.bot.db["Guild settings"].update_one({"_id": ctx.guild.id}, {"$set": {"default role": roleid}})
		await ctx.send("Default role set!")

def setup(bot):
	bot.add_cog(Configuration(bot))