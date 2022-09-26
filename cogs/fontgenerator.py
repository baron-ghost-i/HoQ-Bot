import discord
import datetime
from discord.ext import commands


bold = "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"
italics = "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻0123456789"
bolditalics = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛0123456789"
normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
emoji = ":regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d: :regional_indicator_e: :regional_indicator_f: :regional_indicator_g: :regional_indicator_h: :regional_indicator_i: :regional_indicator_j: :regional_indicator_k: :regional_indicator_l: :regional_indicator_m: :regional_indicator_n: :regional_indicator_o: :regional_indicator_p: :regional_indicator_q: :regional_indicator_r: :regional_indicator_s: :regional_indicator_t: :regional_indicator_u: :regional_indicator_v: :regional_indicator_w: :regional_indicator_x: :regional_indicator_y: :regional_indicator_z: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d: :regional_indicator_e: :regional_indicator_f: :regional_indicator_g: :regional_indicator_h: :regional_indicator_i: :regional_indicator_j: :regional_indicator_k: :regional_indicator_l: :regional_indicator_m: :regional_indicator_n: :regional_indicator_o: :regional_indicator_p: :regional_indicator_q: :regional_indicator_r: :regional_indicator_s: :regional_indicator_t: :regional_indicator_u: :regional_indicator_v: :regional_indicator_w: :regional_indicator_x: :regional_indicator_y: :regional_indicator_z: :zero: :one: :two: :three: :four: :five: :six: :seven: :eight: :nine:"


class Speak(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.normlist = [i for i in normal]
		self.boldlist = [i for i in bold]
		self.italicslist = [i for i in italics]
		self.bolditalics = [i for i in bolditalics]
		self.emojifont = emoji.split()


	#helper function
	async def send_message(self, ctx: commands.Context, message: str):
		if ctx.channel.type == discord.ChannelType.private:
			await ctx.channel.send(message)
		else:
			if ctx.author.nick is not None:
				name = ctx.author.nick
			else:
				name = ctx.author.name
			webhooks = await ctx.channel.webhooks()
			webhook = discord.utils.get(webhooks, name = "HBot")
			if webhook is None:
				webhook = await ctx.channel.create_webhook(name = "HBot")
			await webhook.send(message, username = name, avatar_url = ctx.author.avatar.url)
			await ctx.message.delete()


	@commands.group(aliases = ("say",), invoke_without_command = True)
	async def speak(self, ctx):

		'''Sends a webhook message or a normal message with the specified font'''
		commandlist = list(f"`{i.name}`" for i in self.speak.commands)
		commands = ", ".join(commandlist)
		await ctx.send(embed = discord.Embed(
			description = f'''Proper usage:
`h!speak [option] [message]`
Options available:
{commands}''',
			color = 0x1DACD6, 
			timestamp = datetime.datetime.now()
			))

	@speak.command()
	async def plain(self, ctx: commands.Context, *, args):
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
		await self.send_message(ctx, resp)

	@speak.command()
	async def bbold(self, ctx: commands.Context, *, args):
		'''Converts text to blackboard bold font'''

		l = [j for j in args]
		for i in l:
			if i in self.normlist:
				l[l.index(i)] = self.boldlist[self.normlist.index(i)]
			else:
				pass
		resp = "".join(l)
		await self.send_message(ctx, resp)
		
	@speak.command()
	async def italics(self,ctx: commands.Context, *, args):
		'''Converts text to italics'''

		l = [i for i in args]
		for i in l:
			if i in self.normlist:
				l[l.index(i)] = self.italicslist[self.normlist.index(i)]
			else:
				pass
		resp = "".join(l)
		await self.send_message(ctx, resp)
		
	@speak.command()
	async def bolditalics(self, ctx: commands.Context, *, args):
		'''Converts text to bold and italics format'''

		l = [i for i in args]
		for i in l:
			if i in self.normlist:
				l[l.index(i)] = self.bolditalics[self.normlist.index(i)]
			else:
				pass
		resp = "".join(l)
		await self.send_message(ctx, resp)

	@speak.command()
	async def emojify(self, ctx: commands.Context, *, args):
		'''Converts letters to emojis'''

		l = [j for j in args]
		for i in l:
			if i in self.normlist:
				l[l.index(i)] = self.emojifont[self.normlist.index(i)]
			else:
				pass
		resp = "".join(l)
		await self.send_message(ctx, resp)
	
	@speak.command()
	async def space(self, ctx: commands.Context, *, args):
		'''Adds extra spaces for emphasis'''

		resp = args.replace("", " ")
		await self.send_message(ctx, resp)
			
	@speak.command()
	async def clap(self, ctx: commands.Context, *, args):
		'''Adds 👏 between each word'''
		
		resp = args.replace(" ", "👏")
		await self.send_message(ctx, resp)

async def setup(bot):
	await bot.add_cog(Speak(bot))