import discord
import json
import datetime
from discord.ext import commands
	
class AFK(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def afk(self, ctx, *, args = None):
		'''Sets an AFK message for a user'''
		if args == None:
			afkmsg = "AFK"
		else:
			afkmsg = args
		await ctx.send(embed = discord.Embed(description = f"Set AFK: {afkmsg}", color = 0x00163E, timestamp = datetime.datetime.now()))
		
		afk = {"id": ctx.author.id, "msg": afkmsg}
		with open("data/afk.json", "r") as afklist:
			l1 = json.loads(afklist.read())
			l2 = [i["id"] for i in l1]
		if afk["id"] in l2:
				l1[l2.index(afk["id"])]["msg"] = afk["msg"]
		else:
			l1.append(afk)
		with open("data/afk.json", "w") as afklist:
			afklist.write(json.dumps(l1, indent = 2))
			
	@commands.Cog.listener()
	async def on_message(self, message):
		with open("data/afk.json", "r") as afklist:
			l = json.loads(afklist.read())
		keys = [i["id"] for i in l]
		msgs = [i["msg"] for i in l]

		if message.channel.type == discord.ChannelType.private:
			return

		if message.author.id in keys:
			await message.channel.send(embed = discord.Embed(description = f"{message.author.mention}'s AFK has been removed", color = 0x00DEFF), delete_after = 5)
			l.pop(keys.index(message.author.id))
			with open("data/afk.json", "w+") as afklist:
				afklist.write(json.dumps(l, indent = 2))
		else:
			pass
			
		for user in message.mentions:
			if user == message.author:
				return
			else:
				if user.id in keys:
					await message.channel.send(embed = discord.Embed(description = f"{user.mention} is currently AFK: {msgs[keys.index(user.id)]}", color = 0x73FFA2, timestamp = datetime.datetime.now()))

def setup(bot):
	bot.add_cog(AFK(bot))