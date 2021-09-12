import discord
import asyncio
import json
import datetime
from discord.ext import commands

class Moderation(commands.Cog):
	'''Moderation tools'''
	def __init__(self, bot):
		self.bot = bot
		with open("data/db.json", "r") as fob:
			self.db = json.loads(fob.read())

	def guild_check(ctx):
		if ctx.guild.id == 612234021388156938:
			return True 
		else:
			raise commands.CheckFailure("Cannot use this command on this guild!")
	
	def guildcheck(ctx):
		with open("data/db.json", "r") as foo:
			db = json.loads(foo.read())
		if str(ctx.guild.id) in db.keys():
			return True
		else:
			raise commands.CheckFailure(message = "Add a default role for this guild first, using `h!defaultrole [role]`")

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		with open("data/roles.json", "r") as foo:
			data = json.loads(foo.read())
		roles = [i.id for i in member.roles[1:]]
		data[str(member.guild.id)].update({str(member.id): roles})
		with open("data/roles.json", "w") as foo:
			foo.write(json.dumps(data, indent = 2))

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
	@commands.has_permissions(kick_members = True)
	@commands.check(guild_check)
	async def warn(self, ctx, member: discord.Member, *, reason = "No reason"):
		'''Warns a user. A maximum of three warnings can be provided before user is kicked from server'''
		with open("data/warnings.json", "r") as warns:
			warnings = json.loads(warns.read())
		if str(member.id) not in warnings.keys():
			warning = {f"{member.id}": {"one": f"{reason}", "two": None, "three": None}}
			warnings.update(warning)
			with open("data/warnings.json", "w+") as warns:
				warns.write(json.dumps(warnings))
			await ctx.channel.send(embed = discord.Embed(description = f"**{member} has been warned.**", color = 0xffffff))
		else:
			if warnings[f"{member.id}"]["two"] == None:
				warnings[f"{member.id}"]["two"] = reason
				with open("data/warnings.json", "w+") as warns:
					warns.write(json.dumps(warnings))
				await ctx.channel.send(embed = discord.Embed(description = f"**{member} has been warned for a second time.**", color = 0xffffff))
			else:
				if warnings[f"{member.id}"]["three"] == None:
					warnings[f"{member.id}"]["three"] = reason
					with open("data/warnings.json", "w+") as warns:
						warns.write(json.dumps(warnings))
					await ctx.channel.send(embed = discord.Embed(description = f"**{member} has been warned for a third time.**", color = 0xffffff))
				else:
					await member.kick(reason = reason)
					await ctx.channel.send(embed = discord.Embed(description = f"{member} has been kicked. Reason: {reason}", color = 0xffffff))
					with open("data/warnings.json", "r") as warns:
						warnings = json.loads(warns.read())
					warnings.pop(f"{member.id}")
					with open("data/warnings.json", "w+") as warns:
						warns.write(json.dumps(warnings))

	@commands.command(aliases = ("clear-warn", "clearwarns"))
	@commands.has_permissions(kick_members = True)
	@commands.check(guild_check)
	async def clearwarn(self, ctx, member: discord.Member):
		'''Clears all warnings for a user'''
		if ctx.author.guild_permissions.kick_members:
			with open("data/warnings.json", "r") as warns:
				warnings = json.loads(warns.read())
			if str(member.id) in warnings:
				warnings.pop(str(member.id))
				with open("data/warnings.json", "w+") as warns:
					warns.write(json.dumps(warnings))
				await ctx.channel.send(embed = discord.Embed(description = f"**Cleared all warnings for {member}.**", color = discord.Color.dark_blue()))
			else:
				await ctx.send("Member has no warning!")
		else:
			await ctx.send("You don't have the permission to use that command!")

	@commands.command(aliases = ("show-warns", "show-warn", "warns"))
	@commands.check(guild_check)
	async def warnings(self, ctx, member: discord.Member):
		'''Returns the list of warnings for a given user'''
		with open("data/warnings.json", "r") as warns:
			warnings = json.loads(warns.read())
		if str(member.id) in warnings.keys():
			response = "Warning 1: {} \n Warning 2: {} \n Warning 3: {}".format(warnings[str(member.id)]["one"], warnings[str(member.id)]["two"], warnings[str(member.id)]["three"])
			embed = discord.Embed(description = response, color = discord.Color.dark_blue(), timestamp = datetime.datetime.now(datetime.timezone.utc))
			embed.set_author(name = member, icon_url = member.avatar.url)
			await ctx.channel.send(embed = embed)
		else:
			await ctx.channel.send("Member has no warning!")

	@commands.command(aliases = ("default-role",))
	@commands.has_permissions(administrator = True)
	async def defaultrole(self, ctx: commands.Context, *, role: discord.Role):
		self.db[str(ctx.guild.id)] = role.id
		with open("data/db.json", "w") as foo:
			foo.write(json.dumps(self.db))
		await ctx.send(embed = discord.Embed(description = f"Set default role to {role.mention}", color = 0x00FF77))
	
	@commands.command()
	@commands.has_permissions(manage_roles = True)
	@commands.check(guildcheck)
	async def verify(self, ctx: commands.Context, member: discord.Member, *, name: str = None):
		with open("data/roles.json", "r") as foo:
			data = json.loads(foo.read())
		roles = member.roles
		if str(member.id) in data[str(ctx.guild.id)].keys():
			for i in data[str(ctx.guild.id)][str(member.id)]:
				role = discord.utils.find(lambda role: role.id == i, ctx.guild.roles)
				roles.append(role)
			data[str(ctx.guild.id)].pop(str(member.id))
			with open("data/roles.json", "w") as foo:
				foo.write(json.dumps(data, indent = 2))
			await member.edit(roles = roles, nick = name)
		else:
			id_ = int(self.db[str(ctx.guild.id)])
			role = discord.utils.get(ctx.guild.roles, id = id_)
			roles.append(role)
			if ctx.guild.id == 612234021388156938:
				levelrole = discord.utils.find(lambda role: role.id == 635031667278348289, ctx.guild.roles)
				roles.append(levelrole)
			await member.edit(roles = roles, nick = name)
		await ctx.send("Verified!")

def setup(bot):
	bot.add_cog(Moderation(bot))