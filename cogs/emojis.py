import discord
import inspect
import typing
import datetime
from discord.ext import commands
from utils import paginatorview

class Emojis(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases = ("elist", "emojis"))
	async def emojilist(self, ctx):
		'''Returns the list of emojis available on a server in a message'''
		elist = ctx.guild.emojis
		if len(elist) != 0:
			l = []
			for i in elist:
				if not i.animated:
					l.append(f"<:{i.name}:{i.id}> - `<:{i.name}:{i.id}>`")
				else:
					l.append(f"<a:{i.name}:{i.id}> - `<a:{i.name}:{i.id}>`")
			emojistr = "\n".join(l)
			if len(emojistr) <= 4096:
				await ctx.send(embed = discord.Embed(description = emojistr, timestamp = datetime.datetime.now()))
			else:
				view = paginatorview.View(input = emojistr)
				embed = discord.Embed(description = view.list[0], timestamp = datetime.datetime.now(datetime.timezone.utc))
				embed.set_footer(text = f"Page 1 of {len(view.list)}")
				await ctx.send(embed = embed, view = view)
		else:
			await ctx.channel.send("No emoji on this server")
			
	@commands.command(aliases = ("enlarge", "imagify"))
	async def e(self, ctx, emoji: typing.Union[discord.PartialEmoji, str]):
			'''Returns the image for an emoji'''
			embd = discord.Embed(timestamp = datetime.datetime.now())
			if type(emoji) != str:
				url = emoji.url
			else:
				emote = emoji.encode("unicode_escape").decode()
				u = "\\U000"
				if not emote.startswith("\\u"):
					for i in ["#", "*", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
						if emote.startswith(i):
							if i == "#":
								emote = "23-20e3"
								break
							elif i == "*":
								emote = "2a-20e3"
								break
							else:
								emote = f"3{i}-20e3"
								break
					if u in emote:
						if emote.count(u) == 1:
							emote = emote.replace(u, "").replace("\\ufe0f", "")
						else:
							emote = emote.replace(u, "", 1).replace(u, "-")
				else:
					if emote.count("\\u") == 2:
						emote = emote.replace("\\ufe0f", "")
					emote = emote.replace("\\u", "", 1)
				emote = emote.replace("\\u", "-")
				url = f"https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/{emote}.png"
			try:
				async with self.bot.session.get(url) as req:
					stat = req.status
				assert stat == 200
			except AssertionError:
				raise discord.HTTPException(req, "Emoji not found")
			except:
				raise
			else:
				embd.set_image(url = url)
				await ctx.channel.send(embed = embd)

	@commands.command(aliases = ("enlarge2",))
	async def e2(self, ctx, *, name: str):
		name = name.replace(" ", "_")
		emoji = discord.utils.find(lambda e: e.name.lower() ==  name.lower(), ctx.guild.emojis)
		try:
			assert emoji != None
		except AssertionError:
			raise commands.EmojiNotFound(name)
		except:
			raise
		else:
			embed = discord.Embed(timestamp = discord.utils.utcnow())
			embed.set_image(url = emoji.url)
			await ctx.send(embed = embed)

	@commands.command(aliases = ("addemoji", "addem"))
	@commands.has_permissions(manage_emojis = True)
	async def uploademoji(self, ctx, *args):
		'''Upload emoji to the server'''
		args = list(args)
		try:
			assert args != []
		except AssertionError:
			param = inspect.Parameter("Name", inspect._POSITIONAL_ONLY)
			raise commands.MissingRequiredArgument(param)
		except:
			raise
		else:
			try:
				assert len(ctx.message.attachments) != 0
			except AssertionError:
				try:
					assert args[-1].endswith(".png") or args[-1].endswith(".jpg") or args[-1].endswith(".gif") or args[-1].endswith(".jpeg") or args[-1].endswith(".svg")
				except AssertionError:
					param = inspect.Parameter("Emoji", inspect._POSITIONAL_ONLY)
					raise commands.MissingRequiredArgument(param)
				except:
					raise
				else:
					async with self.bot.session.get(args[-1]) as response:
						em = await response.read()
					name = "_".join(args[:-1])
					try:
						assert len(name) < 32 and len(name) > 1 
					except AssertionError:
						raise commands.UserInputError(message = "Name should be between 2 and 32 characters")
					except:
						raise
					else:
						await ctx.guild.create_custom_emoji(name = name, image = em)
						await ctx.send("Created emoji!")
			else:
				em = await ctx.message.attachments[0].read()
				name = "_".join(args)
				try:
					assert len(name) < 32 and len(name) > 2
				except AssertionError:
					raise commands.UserInputError(message = "Name should be between 2 and 32 characters")
				except:
					raise
				else:
					await ctx.guild.create_custom_emoji(name = name, image = em)
					await ctx.send("Created emoji!")
				
	@commands.command()
	@commands.has_permissions(manage_emojis = True)
	async def steal(self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji], *, name = None):
		'''Duplicates emoji passed in the guild'''
		try:
			bemoji = await emoji.read()
			if name == None:
				name = emoji.name
			else:
				name = name.replace(" ", "_")
			await ctx.guild.create_custom_emoji(name = name, image = bemoji)
			await ctx.channel.send("Created emoji!")
		except:
			raise

def setup(bot):
	bot.add_cog(Emojis(bot))
