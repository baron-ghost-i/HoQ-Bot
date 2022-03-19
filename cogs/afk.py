import discord
import datetime
import asyncio
from discord.ext import commands
	
class AFK(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def afk(self, ctx, *, reason = None):
		'''Sets an AFK message for a user'''
		await asyncio.sleep(0.05)
		afkmsg = reason if reason != None else "AFK"
		try:
			assert self.bot.db["afk"].find_one({"_id": ctx.author.id}) == None
		except AssertionError:
			return
		except:
			raise
		else:
			afk = {"_id": ctx.author.id, "msg": afkmsg}
			self.bot.db["afk"].insert_one(afk)
			await ctx.send(embed = discord.Embed(description = f"Set AFK: {afkmsg}", color = 0x00163E, timestamp = datetime.datetime.now()))
			
	@commands.Cog.listener()
	async def on_message(self, message):
		l = [i for i in self.bot.db["afk"].find()]
		keys = [i["_id"] for i in l]
		msgs = [i["msg"] for i in l]

		if message.channel.type == discord.ChannelType.private:
			return
		
		if message.author.id in keys:
			await message.channel.send(embed = discord.Embed(description = f"{message.author.mention}'s AFK has been removed", color = 0x00DEFF), delete_after = 5)
			self.bot.db['afk'].find_one_and_delete({"_id": message.author.id})
			
		for user in message.mentions:
			if user == message.author:
				return
			else:
				if user.id in keys:
					await message.channel.send(embed = discord.Embed(description = f"{user.mention} is currently AFK: {msgs[keys.index(user.id)]}", color = 0x73FFA2, timestamp = datetime.datetime.now()))

async def setup(bot):
	await bot.add_cog(AFK(bot))