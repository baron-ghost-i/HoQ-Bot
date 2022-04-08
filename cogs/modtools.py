import discord
import asyncio
import datetime
from discord import app_commands
from discord.ext import commands
from utils.utils import *

class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	def guildcheck(ctx):
		if ctx.guild.id in (850039242481991700, 808257138882641960, 839939906558361627, 786520972064587786):
			return False
		check = ctx.bot.db["Guild settings"].find_one({"_id": ctx.guild.id})["default role"]
		if check != None:
			return True
		raise commands.CheckFailure(message = "Add a default role for this guild first, using `h!defaultrole [role]`")

	@commands.Cog.listener()
	async def on_member_remove(self, member: discord.Member):
		if len(member.roles) != 1:
			self.bot.db['roles'].insert_one({'guild': member.guild.id, 'user': member.id, 'roles': [i.id for i in member.roles[1:]]})

	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def purge(self, ctx, *, args = None):
		'''Mass-deletes messages. Default value = 10'''
		if args == None:
			lim = 10
		elif args.isdigit() == True:
			lim = int(args)
		await ctx.channel.purge(limit = lim+1)
		await asyncio.sleep(0.5)
		await ctx.channel.send("Deleted **{}** messages".format(lim), delete_after = 3)
			
	@commands.command()
	@commands.has_permissions(kick_members = True)
	async def kick(self, ctx, user:discord.Member = None, *,reason = None):
		'''Kicks users from server'''
		if user == None or user.guild_permissions.administrator:
			return
		else:
			await user.kick(reason = f"{reason}")
			if reason != None:
				async with ctx.channel.typing():
					await asyncio.sleep(1)
				await ctx.channel.send(embed = discord.Embed(description = f"**{user}** has been kicked from the server. **Reason**: {reason}", color = discord.Color.gold()))
			else:
				async with ctx.channel.typing():
					await asyncio.sleep(1)
				await ctx.channel.send(embed = discord.Embed(description = f"**{user}** has been kicked from the server", color = discord.Color.gold()))
					
	@commands.command()
	@commands.has_permissions(ban_members = True)
	async def ban(self, ctx, user:discord.User = None, *,reason = None):
		'''Bans user from server'''
		banentries = await ctx.guild.bans()
		banlist = [i.user for i in banentries]
		if isinstance(user, discord.Member) and user.guild_permissions.administrator:
			return
		elif user == None:
			return
		elif user in banlist:
			async with ctx.channel.typing():
				await asyncio.sleep(0.5)
			await ctx.channel.send("User is already banned!")
		else:
			await ctx.guild.ban(user, reason = f"{reason}", delete_message_days = 0)
			if reason != None:
				async with ctx.channel.typing():
					await asyncio.sleep(1)
				await ctx.channel.send(embed = discord.Embed(description = f"**{user}** has been banned from the server. **Reason**: {reason}", color = discord.Color.gold()))
			else:
				async with ctx.channel.typing():
					await asyncio.sleep(1)
				await ctx.channel.send(embed = discord.Embed(description = f"**{user}** has been banned from the server", color = discord.Color.gold()))
					
	@commands.command()
	@commands.has_permissions(ban_members = True)
	async def unban(self, ctx, user: discord.User = None, *, reason = None):
		'''Unbans user from server'''
		if user == None:
			return
		else:
			try:
				entry = await ctx.guild.fetch_ban(user)
			except discord.errors.NotFound:
				async with ctx.channel.typing():
					await asyncio.sleep(1)
				await ctx.channel.send("User is not banned!")
			except:
				raise
			else:
				await ctx.guild.unban(entry.user, reason = f"{reason}")
				async with ctx.channel.typing():
					await asyncio.sleep(1)
				await ctx.channel.send(embed = discord.Embed(description = f"**{user}** has been unbanned", color = 0xC0C0C0))
					
	@commands.command()
	@commands.has_permissions(manage_roles = True)
	async def addrole(self, ctx, *args):
		'''Creates a new role with default permissions'''
		args = list(args)
		if "#" in args[-1] and len(args[-1]) == 7:
			color = args[-1].replace("#", "")
			args.pop(-1)
			name = " ".join(args)
			color = int(color, base = 16)
		else:
			color = 0
			name = " ".join(args)
		if name == "":
			name = "new role"
		embd = discord.Embed(description = f"Added role **{name}**", color = color, timestamp = datetime.datetime.now(datetime.timezone.utc))
		await ctx.guild.create_role(name = f"{name}", color = color)
		await ctx.channel.send(embed = embd)
			
	@commands.command()
	@commands.has_permissions(manage_roles = True)
	async def delrole(self, ctx, *, name: discord.Role):
		'''Deletes an existing role'''
		await name.delete()
		await asyncio.sleep(0.5)
		await ctx.channel.send(embed = discord.Embed(description = f"Deleted role {name}", color = discord.Color.gold(), timestamp = datetime.datetime.now()))
	
	@commands.command()
	@commands.has_permissions(manage_roles = True)
	@commands.check(guildcheck)
	async def verify(self, ctx: commands.Context, member: discord.Member, *, name: str = None):
		data = self.bot.db['roles'].find_one_and_delete({'user': member.id})
		roles = []
		if data != None:
			for i in data['roles']:
				role = discord.utils.get(ctx.guild.roles, id = i)
				roles.append(role)
		else:
			id_ = self.bot.db["Guild settings"].find_one({"_id": ctx.guild.id})["default role"]
			role = discord.utils.get(ctx.guild.roles, id = id_)
			roles.append(role)
		await member.edit(roles = roles, nick = name)
		await ctx.send("Verified!")

	@app_commands.command(name='mute', description='Puts a user on timeout. Not specifying any time removes timeout.')
	@app_commands.describe(
		member = 'Member to mute',
		days='Number of days to muting user for (cannot exceed 28 days)',
		hours='Number of hours to mute user for',
		minutes='Number of minutes to mute user for',
		seconds='Number of seconds to mute user for',
		reason='Reason for muting user')
	@app_commands.check(moderatorcheck)
	async def mute(self, interaction: discord.Interaction, member: discord.Member, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, reason: str = None):
		if member.guild_permissions.administrator:
			return await interaction.response.send_message('Cannot mute this member!', ephemeral = True)
			
		t=seconds+(60*minutes)+(60*60*hours)+(60*60*24*days)
		
		if t > 2419200:
			return await interaction.response.send_message("Timeout cannot exceed maximum time limit of 28 days", ephemeral = True)
		if t == 0:
			timeout = None
		else:
			timeout = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()+t).astimezone()
		await member.edit(timed_out_until = timeout, reason = reason)
		await interaction.response.send_message("Member successfully {}! Reason: {}".format("muted" if timeout != None else "unmuted", reason))

async def setup(bot):
	await bot.add_cog(Moderation(bot))