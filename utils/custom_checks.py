import discord
from discord.ext import commands
from typing import Union

Context = Union[commands.Context, discord.Interaction]

def moderatorcheck(ctx: Context) -> bool:
	if isinstance(ctx, commands.Context):
		if ctx.guild == None:
			raise commands.CheckFailure("This command can be used on a guild only!")
		if not (ctx.author.guild_permissions.manage_messages or ctx.author.id == 586088176037265408):
			raise commands.CheckFailure("You don't have the permission to use this command!")
	
	else:
		if ctx.guild == None:
			raise discord.app_commands.CheckFailure("This command can be used on a guild only!")
		if not (ctx.user.guild_permissions.manage_messages or ctx.user.id == 586088176037265408):
			raise discord.app_commands.CheckFailure("You don't have the permission to use this command!")
	return True

def admincheck(ctx: Context) -> bool:
	if isinstance(ctx, commands.Context):
		if ctx.guild == None:
			raise commands.CheckFailure("This command can be used on a guild only!")
		if not (ctx.author.guild_permissions.administrator or ctx.author.id == 586088176037265408 or ctx.guild.owner==ctx.author):
			raise commands.CheckFailure("You don't have the permission to use this command!")
	
	else:
		if ctx.guild == None:
			raise discord.app_commands.CheckFailure("This command can be used on a guild only!")
		if not (ctx.user.guild_permissions.administrator or ctx.user.id == 586088176037265408 or ctx.guild.owner==ctx.user):
			raise discord.app_commands.CheckFailure("You don't have the permission to use this command!")
	return True

def ownercheck(ctx: Context) -> bool:
	if isinstance(ctx, commands.Context):
		user = ctx.author
	else:
		user = ctx.user
	return user.id == 586088176037265408

def isme(ctx: Context) -> bool:
	if isinstance(ctx, commands.Context):
		return ctx.author.id == 586088176037265408
	else:
		return ctx.user.id == 586088176037265408