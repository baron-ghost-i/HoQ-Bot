import discord
import youtube_dl
import asyncio
import functools
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_options = {
	"format": "worst",
	"quiet": True,
	"ignoreerrors": False,
	"source_address": "0.0.0.0",
	"default_search": "auto",
	"skip_download": True
}

ytdl = youtube_dl.YoutubeDL(ytdl_options)

class Audio(discord.PCMVolumeTransformer):
	def __init__(self, source, data, volume = 1.0):
		super().__init__(source, volume)
		self.data = data
		self.title = self.data["title"]
		self.url = self.data["webpage_url"]

	@classmethod
	async def extractor(cls, query, loop):
		loop = loop or asyncio.get_event_loop()
		partial = functools.partial(ytdl.extract_info, query, download = False)
		data = await loop.run_in_executor(None, partial)
		if "entries" in data.keys():
			data = data["entries"][0]
		file = data["url"]
		return cls(discord.FFmpegPCMAudio(file, executable = "/home/vcap/app/ffmpeg-4.4-amd64-static/ffmpeg", options = "-vn"), data = data)

class VoiceState:
	def __init__(self, ctx: commands.Context, query: str, bot: commands.Bot):
		self._ctx = ctx
		self.query = query
		self._loop = False
		self.queue = []
		self.bot = bot
		self.voice = None
		self.next = asyncio.Event()
		self.source = None

	@property
	def loop(self):
		return self._loop
	
	@loop.setter
	def loop(self, value: bool):
		self._loop = value

	@property
	def volume(self):
		return self.source.volume
	
	@volume.setter
	def volume(self, value: float):
		value = int(round(value))
		self.source.volume = value/100

	async def _play(self):
		#will make a queue later
		while True:
			self.next.clear()
			self.source = await Audio.extractor(query = self.query, loop = self.bot.loop)
			self.voice.play(self.source, after = self.after_finish)
			if not self._loop:
				await self._ctx.send(f"Now playing: **{self.source.title}**")
			else:
				await self._ctx.send(f"Now playing: **{self.source.title}**", delete_after = 5.0)
			await self.next.wait()
			self.source.cleanup()
			if self._loop:
				continue
			else:
				break

	def after_finish(self, error = None):
		if error:
			print(error)
		self.next.set()

class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.guild_only()
	async def play(self, ctx: commands.Context, *, query = None):
		ctx.voice_client.voice_state = VoiceState(ctx, query, self.bot)
		ctx.voice_client.voice_state.voice = ctx.voice_client
		try:
			await ctx.voice_client.voice_state._play()
		except:
			raise

	@commands.command(aliases = ("p",))
	@commands.guild_only()
	async def pause(self, ctx: commands.Context):
		if ctx.voice_client.is_playing():
			await ctx.send("Paused!")
			ctx.voice_client.pause()
		elif ctx.voice_client.is_paused():
			await ctx.send("Playing!")
			ctx.voice_client.resume()
		else:
			await ctx.send("Not playing anything!")

	@commands.command()
	@commands.guild_only()
	async def stop(self, ctx: commands.Context):
		if ctx.voice_client.is_playing():
			ctx.voice_client.voice_state.loop = False
			ctx.voice_client.stop()
			await ctx.send("Current song has been stopped!")
		else:
			await ctx.send("Not playing anything!")

	@commands.command()
	async def loop(self, ctx):
		if ctx.voice_client.is_playing():
			ctx.voice_client.voice_state.loop = not ctx.voice_client.voice_state.loop
			if ctx.voice_client.voice_state.loop:
				await ctx.send("Now looping the current song!")
			else:
				await ctx.send("Loop disabled!")
		else:
			return

	@commands.command(aliases = ("join",))
	@play.before_invoke
	async def connect(self, ctx):
		if ctx.voice_client != None:
			return
		if ctx.author.voice == None:
			await ctx.send("Connect to a voice channel first!")
		else:
			await ctx.author.voice.channel.connect(timeout = 180.0)
			await ctx.send(f"Connected to **{ctx.guild.voice_client.channel}**")

	@commands.command(aliases = ("leave", "dc"))
	@commands.guild_only()
	async def disconnect(self, ctx):
		if ctx.guild.voice_client.is_connected():
			await ctx.voice_client.disconnect()
			await ctx.send("Disconnected!")
		else:
			await ctx.send("Not connected to any voice channel")

	@commands.command(aliases = ("vol",))
	async def volume(self, ctx, value):
		if ctx.guild.voice_client.is_connected():
			try:
				assert value.isdigit()
				assert 0 <= int(value) <= 100
			except AssertionError:
				await ctx.send("Please provide a valid integer value for volume, between 0 and 100")
			else:
				ctx.voice_client.voice_state.volume = int(value)
				await ctx.send(f"Set the volume to **{value}%**") 
		else:
			await ctx.send("Not connected to any voice channel")

def setup(bot):
	bot.add_cog(Music(bot))