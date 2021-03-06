import discord
import datetime
from discord.ext import commands

class Speak(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		bold = "๐ธ๐นโ๐ป๐ผ๐ฝ๐พโ๐๐๐๐๐โ๐โโโ๐๐๐๐๐๐๐โค๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐ ๐ก๐ข๐ฃ๐ค๐ฅ๐ฆ๐ง๐จ๐ฉ๐ช๐ซ๐๐๐๐๐๐๐๐๐ ๐ก"
		italics = "๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐ ๐ก๐ข๐ฃ๐ค๐ฅ๐ฆ๐ง๐จ๐ฉ๐ช๐ซ๐ฌ๐ญ๐ฎ๐ฏ๐ฐ๐ฑ๐ฒ๐ณ๐ด๐ต๐ถ๐ท๐ธ๐น๐บ๐ป0123456789"
		bolditalics = "๐จ๐ฉ๐ช๐ซ๐ฌ๐ญ๐ฎ๐ฏ๐ฐ๐ฑ๐ฒ๐ณ๐ด๐ต๐ถ๐ท๐ธ๐น๐บ๐ป๐ผ๐ฝ๐พ๐ฟ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐0123456789"
		normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		emoji = ":regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d: :regional_indicator_e: :regional_indicator_f: :regional_indicator_g: :regional_indicator_h: :regional_indicator_i: :regional_indicator_j: :regional_indicator_k: :regional_indicator_l: :regional_indicator_m: :regional_indicator_n: :regional_indicator_o: :regional_indicator_p: :regional_indicator_q: :regional_indicator_r: :regional_indicator_s: :regional_indicator_t: :regional_indicator_u: :regional_indicator_v: :regional_indicator_w: :regional_indicator_x: :regional_indicator_y: :regional_indicator_z: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d: :regional_indicator_e: :regional_indicator_f: :regional_indicator_g: :regional_indicator_h: :regional_indicator_i: :regional_indicator_j: :regional_indicator_k: :regional_indicator_l: :regional_indicator_m: :regional_indicator_n: :regional_indicator_o: :regional_indicator_p: :regional_indicator_q: :regional_indicator_r: :regional_indicator_s: :regional_indicator_t: :regional_indicator_u: :regional_indicator_v: :regional_indicator_w: :regional_indicator_x: :regional_indicator_y: :regional_indicator_z: :zero: :one: :two: :three: :four: :five: :six: :seven: :eight: :nine:"
		self.normlist = [i for i in normal]
		self.boldlist = [i for i in bold]
		self.italicslist = [i for i in italics]
		self.bolditalics = [i for i in bolditalics]
		self.emojifont = emoji.split()

	@commands.group(aliases = ("say",), invoke_without_command = True)
	async def speak(self, ctx):
		'''Sends a webhook message or a normal message with the specified font'''
		commandlist = list(f"`{i.name}`" for i in self.speak.commands)
		commands = ", ".join(commandlist)
		await ctx.send(embed = discord.Embed(description = f'''Proper usage:
`h!speak [option] [message]`
Options available:
{commands}''', color = 0x1DACD6, timestamp = datetime.datetime.now()))

	@speak.command()
	async def plain(self, ctx, *, args):
		'''Converts a text to plain'''
		l = [j for j in args]
		for i in l:
			if i in self.boldlist:
				l[l.index(i)] = self.normlist[self.boldlist.index(i)]
			elif i in self.italicslist:
				l[l.index(i)] = self.normlist[self.italicslist.index(i)]
			elif i in self.bolditalics:
				l[l.index(i)] = self.normlist[self.bolditalics.index(i)]
			elif i in self.emojifont:
				l[l.index(i)] = self.normlist(self.emojifont.index(i))
			else:
				pass
		resp = "".join(l)
		if ctx.channel.type == discord.ChannelType.private:
			await ctx.channel.send(resp)
		else:
			if ctx.author.nick != None:
				name = ctx.author.nick
			else:
				name = ctx.author.name
			webhooks = await ctx.channel.webhooks()
			webhook = discord.utils.get(webhooks, name = "HBot")
			if webhook == None:
				webhook = await ctx.channel.create_webhook(name = "HBot")
			await webhook.send(resp, username = name, avatar_url = ctx.author.avatar.url)
			await ctx.message.delete()

	@speak.command()
	async def bbold(self, ctx, *, args):
		'''Converts text to blackboard bold font'''
		l = [j for j in args]
		for i in l:
			if i in self.normlist:
				l[l.index(i)] = self.boldlist[self.normlist.index(i)]
			else:
				pass
		resp = "".join(l)
		if ctx.channel.type == discord.ChannelType.private:
			await ctx.channel.send(resp)
		else:
			if ctx.author.nick != None:
				name = ctx.author.nick
			else:
				name = ctx.author.name
			webhooks = await ctx.channel.webhooks()
			webhook = discord.utils.get(webhooks, name = "HBot")
			if webhook == None:
				webhook = await ctx.channel.create_webhook(name = "HBot")
			await webhook.send(resp, username = name, avatar_url = ctx.author.avatar.url)
			await ctx.message.delete()
		
	@speak.command()
	async def italics(self,ctx, *, args):
		'''Converts text to italics'''
		l = [i for i in args]
		for i in l:
			if i in self.normlist:
				l[l.index(i)] = self.italicslist[self.normlist.index(i)]
			else:
				pass
		resp = "".join(l)
		if ctx.channel.type == discord.ChannelType.private:
			await ctx.channel.send(resp)
		else:
			if ctx.author.nick != None:
				name = ctx.author.nick
			else:
				name = ctx.author.name
			webhooks = await ctx.channel.webhooks()
			webhook = discord.utils.get(webhooks, name = "HBot")
			if webhook == None:
				webhook = await ctx.channel.create_webhook(name = "HBot")
			await webhook.send(resp, username = name, avatar_url = ctx.author.avatar.url)
			await ctx.message.delete()
		
	@speak.command()
	async def bolditalics(self, ctx, *, args):
		'''Converts text to bold and italics format'''
		l = [i for i in args]
		for i in l:
			if i in self.normlist:
				l[l.index(i)] = self.bolditalics[self.normlist.index(i)]
			else:
				pass
		resp = "".join(l)
		if ctx.channel.type == discord.ChannelType.private:
			await ctx.channel.send(resp)
		else:
			if ctx.author.nick != None:
				name = ctx.author.nick
			else:
				name = ctx.author.name
			webhooks = await ctx.channel.webhooks()
			webhook = discord.utils.get(webhooks, name = "HBot")
			if webhook == None:
				webhook = await ctx.channel.create_webhook(name = "HBot")
			await webhook.send(resp, username = name, avatar_url = ctx.author.avatar.url)
			await ctx.message.delete()

	@speak.command()
	async def emojify(self, ctx, *, args):
		'''Converts letters to emojis'''
		l = [j for j in args]
		for i in l:
			if i in self.normlist:
				l[l.index(i)] = self.emojifont[self.normlist.index(i)]
			else:
				pass
		resp = "".join(l)
		if ctx.channel.type == discord.ChannelType.private:
			await ctx.channel.send(resp)
		else:
			if ctx.author.nick != None:
				name = ctx.author.nick
			else:
				name = ctx.author.name
			webhooks = await ctx.channel.webhooks()
			webhook = discord.utils.get(webhooks, name = "HBot")
			if webhook == None:
				webhook = await ctx.channel.create_webhook(name = "HBot")
			await webhook.send(resp, username = name, avatar_url = ctx.author.avatar.url)
			await ctx.message.delete()
	
	@speak.command()
	async def space(self, ctx, *, args):
		'''Adds extra spaces for emphasis'''
		resp = args.replace("", " ")
		if ctx.channel.type == discord.ChannelType.private:
			await ctx.channel.send(resp)
		else:
			if ctx.author.nick != None:
				name = ctx.author.nick
			else:
				name = ctx.author.name
			webhooks = await ctx.channel.webhooks()
			webhook = discord.utils.get(webhooks, name = "HBot")
			if webhook == None:
				webhook = await ctx.channel.create_webhook(name = "HBot")
			await webhook.send(resp, username = name, avatar_url = ctx.author.avatar.url)
			await ctx.message.delete()
			
	@speak.command()
	async def clap(self, ctx, *, args):
		'''Adds ๐ between each word'''
		resp = args.replace(" ", "๐")
		if ctx.channel.type == discord.ChannelType.private:
			await ctx.channel.send(resp)
		else:
			if ctx.author.nick != None:
				name = ctx.author.nick
			else:
				name = ctx.author.name
			webhooks = await ctx.channel.webhooks()
			webhook = discord.utils.get(webhooks, name = "HBot")
			if webhook == None:
				webhook = await ctx.channel.create_webhook(name = "HBot")
			await webhook.send(resp, username = name, avatar_url = ctx.author.avatar.url)
			await ctx.message.delete()

async def setup(bot):
	await bot.add_cog(Speak(bot))