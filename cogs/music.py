import discord
import youtube_dl
import asyncio
import itertools
import datetime

from discord.ext import commands
from async_timeout import timeout
from typing import (
    Union,
    Optional
)

from utils.utils import to_discord_timestamp


youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_options = {
	'format': 'bestaudio/worstaudio/worst/best',
	'quiet': True,
	'ignoreerrors': False,
	'source_address': '0.0.0.0',
	'default_search': 'auto',
    'keepvideo': False,
    'skip_download': True
}


ytdl = youtube_dl.YoutubeDL(ytdl_options)


class VoiceError(Exception):
    '''To be raised by voice-related errors'''


class YTDLError(Exception):
    '''To be raised by YouTubeDL if required'''


class Song(discord.PCMVolumeTransformer):

    def __init__(self, source: discord.FFmpegPCMAudio, data: dict, ctx: commands.Context, volume: float = 1.0):
        super().__init__(source, volume)
        self.rawdata: dict = data
        date = self.rawdata.get('upload_date')
        date = datetime.datetime(year = int(date[:4]), month = int(date[4:6]), day = int(date[6:]))
        date = to_discord_timestamp(date, date_only = True)
        self.processed_data: dict = {
            'thumbnail': self.rawdata.get('thumbnail'),
            'title': self.rawdata.get('title'),
            'url': self.rawdata.get('webpage_url'),
            'duration': self.get_duration(int(self.rawdata.get('duration'))),
            'uploader': (self.rawdata.get('uploader'), self.rawdata.get('uploader_url')),
            'upload_date': date
        }
        self.ctx = ctx

        try:
            assert (self.processed_data['title'] is not None and self.processed_data['url'] is not None)
        except AssertionError:
            raise YTDLError('An unexpected error occurred while trying to fetch the song!')
        except:
            raise

    @classmethod
    async def extract(cls, ctx: commands.Context, query: str, loop: asyncio.AbstractEventLoop = None, download: bool = False):
        loop = loop or asyncio.get_event_loop()

        data = await loop.run_in_executor(None, ytdl.extract_info, query, download)

        if data is None or data == {}:
            raise YTDLError('Could not find a match! Try using a different query.')

        if 'entries' in data.keys():
            for entry in data['entries']:
                if entry:
                    data = entry
                    break
        source = discord.FFmpegPCMAudio(data['url'], executable = '/home/vcap/app/ffmpeg-4.4-amd64-static/ffmpeg', options='-vn')
        return cls(source, data, ctx)

    def get_duration(self, duration: int) -> str:
        if duration is None:
            return None

        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration_str = f"{minutes} minutes, {seconds} seconds"

        if bool(hours):
            duration_str = f'{hours} hours, ' + duration_str

        if bool(days):
            duration_str = f'{days} days, ' + duration_str

        return duration_str
    
    async def discord_embed(self, flag: bool = False):
        if flag:
            title = '**Queued**'
        else:
            title = '**Now playing**'
        embed = discord.Embed(
            color = 0x00FF77,
            title = title,
            description = f'[{self.processed_data["title"]}]({self.processed_data["url"]})',
            timestamp = discord.utils.utcnow()
            )
        embed.set_thumbnail(url = self.processed_data['thumbnail'])
        embed.add_field(name = 'Duration', value = self.processed_data['duration'], inline = False)
        embed.add_field(name = 'Uploaded By', value = f'[{self.processed_data["uploader"][0]}]({self.processed_data["uploader"][1]})')
        embed.add_field(name = 'Uploaded On', value = self.processed_data['Upload_date'])
        embed.add_field(name = 'Requested By', value = self.ctx.author.mention, inline = False)

        return embed


class Playlist(asyncio.Queue):

    def __getitem__(self, key):
        if isinstance(key, slice):
            return list(itertools.islice(self._queue, key.start, key.stop, key.step))
        else:
            return self._queue[key]

    def __len__(self) -> int:
        return self.qsize

    def __iter__(self):
        return self._queue.__iter__()

    def clear(self):
        self._queue.clear()

class Player:

    def __init__(self, ctx: commands.Context, bot: commands.Bot):
        self.ctx = ctx
        self.guild: int = self.ctx.guild.id
        self.playlist: Playlist = Playlist(20)
        self.bot = bot
        self.vc: discord.VoiceClient = self.ctx.guild.voice_client
        self.next: asyncio.Event = asyncio.Event()
        self._loop: bool = False
        self.current: Optional[Song] = None
        self.bot.loop.create_task(self.play_song())

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self.current.volume

    @volume.setter
    def volume(self, vol: int):
        self.current.volume = vol/100

    async def play_song(self) -> None:
        while True:
            self.next.clear()
            if not self.loop:
                try:
                    async with timeout(180.0):
                        self.current: Song = await self.playlist.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop(flag = True))
                    return
                except:
                    raise
            else:
                if self.current:
                    self.current: Song = await Song.extract(ctx = self.current.ctx, query = self.current.processed_data['url'])

            await self.ctx.send(embed = await self.current.discord_embed(), delete_after = 10.0)
            self.vc.play(self.current, after = self.play_next)
            await self.next.wait()

    def play_next(self, error = None):
        if error:
            raise VoiceError(str(error))
        self.next.set()

    async def stop(self, flag: bool = False):
        self.playlist.clear()
        self.vc.stop()
        if flag and self.vc:
            await self.vc.disconnect()

    async def enqueue(self, query: str):
        if not self.playlist.full():
            song = await Song.extract(self.ctx, query, download = False)
            await self.playlist.put(song)
        else:
            raise asyncio.QueueFull('Cannot add more items to the playlist!')
        
    async def dequeue(self):
        if not self.playlist.empty():
            return await self.playlist.get()
        else:
            raise asyncio.QueueEmpty('Playlist is empty!')


players = {}


class Music(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage('Cannot use this command outside a guild!')
        return True

    def get_player(self, ctx: commands.Context) -> Player:
        if ctx.guild.id in players.keys():
            return players[ctx.guild.id]
        else:
            players[ctx.guild.id] = Player(ctx, self.bot)
            return players[ctx.guild.id]

    def delete_player(self, ctx: commands.Context) -> Player:
        return players.pop(ctx.guild.id)

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        player = self.get_player(ctx)
        if player.vc.is_paused():
            return player.vc.resume()
        await player.enqueue(query)

    @commands.command(aliases = ('p',))
    async def pause(self, ctx: commands.Context):
        player = self.get_player(ctx)
        if not player.vc.is_paused():
            player.vc.pause()
        else:
            player.vc.resume()
    
    @commands.command()
    async def stop(self, ctx: commands.Context):
        player = self.get_player(ctx)
        await player.stop()

    @commands.command()
    async def loop(self, ctx: commands.Context):
        player = self.get_player(ctx)
        player.loop = not player.loop
        msg = "Looping the current song!" if player.loop else "Loop disabled!"
        await ctx.send(msg)

    @commands.command(aliases = ("join",))
    @play.before_invoke
    async def connect(self, ctx: commands.Context):
        if ctx.author.voice is None:
            await ctx.send("Connect to a voice channel first!")
        elif ctx.voice_client is not None:
            if ctx.voice_client.channel.members != [] and ctx.voice_client.is_playing():
                await ctx.send("Can't switch vc while others are listening!")
            else:
                pass
        else:
            await ctx.author.voice.channel.connect(timeout = 180.0)
            player = self.get_player(ctx)
            await ctx.send(f'Connected to channel **{player.vc.channel}**')


    @commands.command(aliases = ('dc',))
    async def disconnect(self, ctx: commands.Context):
        if ctx.voice_client is None:
            return await ctx.send('Not connected to any voice channel!')
        if ctx.voice_client.is_playing():
            player = self.get_player(ctx)
            await player.stop()
        await ctx.voice_client.disconnect()
        self.delete_player(ctx)
        await ctx.send('Disconnected!')

    @commands.command(aliases = ('np',))
    async def now_playing(self, ctx):
        player = self.get_player(ctx)
        if player.vc.is_playing():
            await ctx.send(embed = await player.current.discord_embed(True))

#to be created later
class MusicPlayer(discord.ui.View):

    def __init__(self, queue: Playlist, client: discord.VoiceClient, listener: Union[discord.Member, discord.User]):
        super().__init__(timeout=None)
        self.playlist = queue
        self.vc = client
        self._listener = listener

    @discord.ui.button()
    async def previous(self, interaction, button):
        pass

    @discord.ui.button()
    async def play(self, interaction, button):
        pass

    @discord.ui.button()
    async def pause(self, interaction, button):
        pass

    @discord.ui.button()
    async def next(self, interaction, button):
        pass

    @discord.ui.button()
    async def stop(self, interaction, button):
        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))