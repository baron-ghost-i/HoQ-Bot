import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(embed = discord.Embed(description = f"Missing argument: {error.param.name}", color = discord.Color.red()))
            
        elif isinstance(error, commands.CommandInvokeError):
            err = error.original
            if isinstance(err, discord.HTTPException):
                await ctx.reply(embed = discord.Embed(description = f"{err.status}: {err.text}", color = discord.Color.red()))
            else:
                user = self.get_user(586088176037265408)
                await user.send(str(err))
		
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.reply(embed = discord.Embed(description = "Use this command in DMs!", color = discord.Color.red()))
		
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(embed = discord.Embed(description = f"Command is on cooldown! Try again after {round(error.retry_after, 2)} seconds", color = discord.Color.red()))
		
        elif isinstance(error, commands.NotOwner) or isinstance(error, commands.MissingPermissions):
            await ctx.reply(embed = discord.Embed(description = "You do not have the permission to use this command!", color = discord.Color.red()))
        
        elif isinstance(error, commands.BadUnionArgument):
            await ctx.reply(embed = discord.Embed(description = "Error: conversion failed, please check the input provided.", color = discord.Color.red()))
            
        elif isinstance(error, commands.UserInputError):
            await ctx.reply(embed = discord.Embed(description = f"Input error: {error}", color = discord.Color.red()))
            
        elif isinstance(error, commands.UserNotFound):
            await ctx.reply(embed = discord.Embed(description = "Error: User not found", color = discord.Color.red()))
		
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(embed = discord.Embed(description = f"{error}", color = discord.Color.red()))

async def setup(bot):
    await bot.add_cog(ErrorHandler)