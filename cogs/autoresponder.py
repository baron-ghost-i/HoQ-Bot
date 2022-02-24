import re
import asyncio
import datetime

import discord
from discord.ext import commands

from utils.utils import (
	guildid,
	admincheck,
	PaginatorView
	)


class Autoresponder(commands.Cog):

	
	def __init__(self, bot):
		self.bot = bot

		
	@commands.command(aliases = ('addresp',))
	@commands.guild_only()
	@admincheck()
	async def addresponse(self, ctx, trigger, response, wildcard = None):
		if any(["__" in response, "lambda" in response]):
			await ctx.send("Cannot add that autoresponse")
			return

		id = guildid(ctx.guild.id)
		if wildcard == None or wildcard.lower() != "wildcard":
			wildcard = False
		else:
			wildcard = True
		self.bot.db['autoresponder'].insert_one({
			'guild': id,
			'wildcard': wildcard,
			'trigger': trigger,
			'response': response
		})
		await ctx.send("Autoresponse successfully added")

			
	@commands.command(aliases = ('removeresp',))
	@commands.guild_only()
	@admincheck()
	async def removeresponse(self, ctx, *, trigger):
		id = guildid(ctx.guild.id)
		out = self.bot.db['autoresponder'].find_one_and_delete({
			'guild': id,
			'trigger': trigger
		})
		try:
			assert out != None
		except AssertionError:
			await ctx.send("No such trigger found")
		except:
			raise
		else:
			await ctx.send("Trigger successfully removed")

			
	@commands.command(aliases = ('responses', 'resps'))
	@commands.guild_only()
	async def responselist(self, ctx):
		id = guildid(ctx.guild.id)
		if self.bot.db['autoresponder'].count_documents({"guild": id}) == 0:
			return await ctx.send("No autoresponse on this guild")

		wild = ""
		norm = ""
		for i in self.bot.db['autoresponder'].find({'guild': id}):
			if i['wildcard'] == True:
				wild += f"• `\"{i['trigger']}\"` — `\"{i['response']}\"`"
			else:
				norm += f"• `\"{i['trigger']}\"` — `\"{i['response']}\"`"

		outstr = "__**Normal autoresponses:**__\n\n {} \n\n __**Wildcards:**__\n\n {}".format(norm, wild)

		if len(outstr) <= 4096:
			await ctx.send(embed = discord.Embed(description = outstr, color = 0x00FF77, timestamp = datetime.datetime.now()))
			return
			
		view = PaginatorView(input = outstr)
		embed = discord.Embed(description = view.list[0], timestamp = datetime.datetime.now())
		embed.set_footer(text = f"Page 1 of {len(view.list)}")
		await ctx.send(embed = embed, view = view)
		
				
	@commands.Cog.listener()
	async def on_message(self, message):
		
		if message.guild == None:
			return
			
		id = guildid(message.guild.id)
		check = self.bot.db['Guild settings'].find_one({'_id': id})['autoresponder']
		
		if (not check) or message.author.bot:
			return
			
		dcheck = self.bot.db['Guild settings'].find_one({'_id': id})['dadmode']

		msg = re.sub('[.,;:?!/\-\'\"]', '', message.content).lower()

		normal = [(i['trigger'], i['response']) for i in self.bot.db['autoresponder'].find({'guild': id, 'wildcard': False})]
		wild = [(i['trigger'], i['response']) for i in self.bot.db['autoresponder'].find({'guild': id, 'wildcard': True})]

		for i in normal:
			if message.content.lower() == i[0].lower():
				async with message.channel.typing():
					await asyncio.sleep(0.5)
					return await message.reply(i[1])

		for i in wild:
			if (msg.startswith(f"{i[0]} ")) or (msg.endswith(f" {i[0]}")) or (f" {i[0]} " in msg) or (msg == i[0]):
				async with message.channel.typing():
					await asyncio.sleep(0.5)
					return await message.reply(i[1])

		if any([" i'm " in msg, " im " in msg, " i am " in msg, msg.startswith('im '), msg.startswith("i'm "), msg.startswith('i am ')]) and dcheck and len(msg) <= 2035:
			pos = None
			for i in ["im", "i am", "i'm"]:
				match = re.match(i, msg)
				if match != None:
					pos = match.end()
					break
			if pos != None:
				reply = f"Hi{msg[pos:]}, I\'m dad!"
				async with message.channel.typing():
					await asyncio.sleep(0.5)
					return await message.reply(reply)
	
	@commands.Cog.listener()
	async def on_member_join(self, member):
		if member.guild.id == 612234021388156938:
			channel = self.bot.get_channel(612251604132823071)
			await channel.send(f'''Welcome to HoQ {member.mention}! To get verified, post a link to your Quora account. If you do not have a Quora account, let us know how you found the server.
Thank you for your patience! A moderator will verify you shortly.''')

def setup(bot):
	bot.add_cog(Autoresponder(bot))