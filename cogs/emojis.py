import discord
import inspect
import typing
import datetime
import cairosvg

from io import BytesIO
from PIL import Image
from discord import app_commands
from discord.ext import commands
from utils import PaginatorView

class Emojis(commands.Cog):
	def __init__(self, bot):
		self.bot: commands.Bot = bot

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
				view = PaginatorView(input = emojistr)
				embed = discord.Embed(description = view.list[0], timestamp = datetime.datetime.now(datetime.timezone.utc))
				embed.set_footer(text = f"Page 1 of {len(view.list)}")
				await ctx.send(embed = embed, view = view)
		else:
			await ctx.channel.send("No emoji on this server")

	async def get_emoji(self, emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str], from_name: bool, size: int = 256):
		embed = discord.Embed(timestamp = datetime.datetime.now())
		if not isinstance(emoji, str):
			name = emoji.name
			url = emoji.url

		else:
			if from_name:
				emote = emoji.replace(" ", "_")
				emoji = discord.utils.find(lambda e: e.name.lower() == emote.lower(), self.bot.emojis)
				try:
					assert emoji != None
				except AssertionError:
					raise commands.EmojiNotFound(emote)
				except:
					raise
				else:
					name = emoji.name
					url = emoji.url
			
			else:
				name = "emoji"
				emote = emoji.encode("unicode_escape").decode()
				u = "\\U000"
				if not emote.startswith("\\u"):
					if emote.startswith('#'):
						emote = '23-20e3'
					elif emote.startswith('*'):
						emote = '2a-20e3'
					elif emote[0].isdigit():
						emote = f'3{emote[0]}-20e3'
					else:
						pass

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
				url = f"https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/{emote}.svg"
				
		if name != 'emoji' and emoji.animated:
			embed.set_image(url=url)
			embed.set_footer(text = '90×90')
			return embed

		try:
			async with self.bot.session.get(url) as req:
				stat = req.status
				data = await req.read()
				assert stat == 200
		except AssertionError:
			raise discord.HTTPException(req, "Emoji not found")
		except:
			raise
		else:
			fp = BytesIO()
			if "twemoji" in url:
				data = data.replace(b'<svg ', bytes(f'<svg width="{size}px" height="{size}px" ', 'utf-8'))
				cairosvg.svg2png(file_obj=BytesIO(data), write_to=fp)
				dim = (size, size)
			else:
				original = Image.open(BytesIO(data))
				final = original.resize((size, original.height*size//original.width), resample=Image.Resampling(1))
				final.save(fp, format='PNG')
				dim = (final.width, final.height)
			fp.seek(0)
			file = discord.File(fp, filename = f"{name}.png")
			embed.set_image(url = f"attachment://{name}.png")
			embed.set_footer(text=f'{dim[0]}×{dim[1]}')
			return (embed, file)

	@commands.command(aliases = ("e",))
	async def enlarge(self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str], size: int = 256):
		'''Returns the image for an emoji'''
		result = await self.get_emoji(emoji = emoji, from_name = False, size = size)
		if isinstance(result, discord.Embed):
			await ctx.send(embed=result)
		else:
			await ctx.send(embed=result[0], file=result[1])

	@commands.command(aliases = ("e2",))
	async def enlarge_from_name(self, ctx, name: str, size: int = 256):
		result = await self.get_emoji(emoji=name, from_name = True, size = size)
		if isinstance(result, discord.Embed):
			await ctx.send(embed=result)
		else:
			await ctx.send(embed=result[0], file = result[1])

	@app_commands.command(name='enlarge', description='Returns a custom emoji in PNG or GIF format')
	@app_commands.describe(emoji='Name of the emoji to be shown',
	size='Size of the image (if static). Defaults to 256 px width')
	async def _enlarge(self, interaction: discord.Interaction, emoji: str, size: int = 256):
		result = await self.get_emoji(emoji=emoji, from_name = True)
		if isinstance(result, discord.Embed):
			await interaction.response.send_message(embed=result)
		else:
			await interaction.response.send_message(embed=result[0], file=result[1])

	@_enlarge.autocomplete(name='emoji')
	async def enlarge_autocomplete(self, interaction: discord.Interaction, current: str):
		emojis = list(self.bot.emojis)
		if current == '':
			return emojis[:25]

		choicelist = [
			app_commands.Choice(name = emoji.name, value = emoji.name) for emoji in emojis if current in emoji.name
			]
		if len(choicelist) > 25:
			choicelist = choicelist[:25]
		return choicelist

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

async def setup(bot):
	await bot.add_cog(Emojis(bot))