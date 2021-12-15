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
		if message.author.bot: 
			return
		data = {id: message}
		if id not in self.snipelist.keys():
			self.snipelist.update(data)
		else:
			self.snipelist[id] = message
		await asyncio.sleep(90.0)
		if id in self.snipelist.keys() and self.snipelist[id] == message:
			self.snipelist.pop(id)

			
		
	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		if before.author.bot:
			return
		id = before.channel.id
		data = {id: (before, after)}
		if id not in self.editsnipelist.keys():
			self.editsnipelist.update(data)
		else:
			self.editsnipelist[id] = (before, after)
		await asyncio.sleep(90.0)
		if id in self.editsnipelist and self.editsnipelist[id] == (before, after):
			self.editsnipelist.pop(id)
				
	@commands.command()
	async def snipe(self, ctx):
		if ctx.channel.id in self.snipelist.keys():
			msg = self.snipelist[ctx.channel.id]
			embed = discord.Embed(description = msg.content, color = 0x00FF77, timestamp = msg.created_at.timestamp())
			embed.set_author(name = msg.author, icon_url = msg.author.avatar.url)
			embed.set_footer(text = f"Requested by {ctx.author}")
			await ctx.send(embed = embed)
		else:
			await ctx.send("There is nothing to snipe!")

	@commands.command()
	async def editsnipe(self, ctx):
		if ctx.channel.id in self.editsnipelist.keys():
			before, after = self.editsnipelist[ctx.channel.id]
			embed = discord.Embed(color = 0x00FF77, timestamp = before.edited_at.timestamp())
			embed.add_field(name = "Before", value = before)
			embed.add_field(name = "After", value = after)
			embed.set_author(name = before.author, icon_url = before.author.avatar.url)
			await ctx.send(embed = embed)
		else:
			await ctx.send("There is nothing to snipe!")

def setup(bot):
	bot.add_cog(MessageSnipe(bot))