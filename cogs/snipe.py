import discord
import asyncio
import datetime
from discord.ext import commands

class MessageSnipe(commands.Cog):
	def __init__(self, bot):
		self.bot = bot 
		self.snipelist = {}
		self.editsnipelist = {}
	
	@commands.Cog.listener()
	async def on_message_delete(self, message): 
		id = message.channel.id
		if not message.author.bot: 
			data = {id: message}
			self.snipelist.update(data)
			await asyncio.sleep(90.0)
			if id in self.snipelist.keys():
				self.snipelist.pop(id)
		
	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if not before.author.bot:
			id = before.channel.id
			data = {id: before}
			self.editsnipelist.update(data)
			await asyncio.sleep(90.0)
			if id in self.editsnipelist:
				self.editsnipelist.pop(id)
				
	@commands.command()
	async def snipe(self, ctx):
		if ctx.channel.id in self.snipelist.keys():
			msg = self.snipelist[ctx.channel.id]
			embed = discord.Embed(description = msg.content, color = 0x00FF77, timestamp = datetime.datetime.now())
			embed.set_author(name = msg.author, icon_url = msg.author.avatar.url)
			embed.set_footer(text = f"Requested by {ctx.author}")
			await ctx.send(embed = embed)
		else:
			await ctx.send("There is nothing to snipe!")

	@commands.command()
	async def editsnipe(self, ctx):
		if ctx.channel.id in self.editsnipelist.keys():
			msg = self.editsnipelist[ctx.channel.id]
			embed = discord.Embed(description = msg.content, color = 0x00FF77, timestamp = datetime.datetime.now())
			embed.set_author(name = msg.author, icon_url = msg.author.avatar.url)
			embed.set_footer(text = f"Requested by {ctx.author}")
			await ctx.send(embed = embed)
		else:
			await ctx.send("There is nothing to snipe!")

def setup(bot):
	bot.add_cog(MessageSnipe(bot))