from discord.app_commands import CheckFailure
from discord import Embed, Color, HTTPException
from discord.ext import commands
from discord import Interaction
from discord.app_commands import AppCommandError, CommandInvokeError

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        user = self.bot.get_user(586088176037265408)

        if isinstance(error, commands.CommandNotFound):
            pass
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(embed = Embed(description = f"Missing argument: {error.param.name}", color = Color.red()))
            
        elif isinstance(error, commands.CommandInvokeError):
            err = error.original
            if isinstance(err, HTTPException):
                await ctx.reply(embed = Embed(description = f"{err.status}: {err.text}", color = Color.red()))
                await user.send(str(await err.response.text()))
            else:
                await user.send(str(err))
		
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.reply(embed = Embed(description = "Use this command in DMs!", color = Color.red()))
		
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(embed = Embed(description = f"Command is on cooldown! Try again after {round(error.retry_after, 2)} seconds", color = Color.red()))
		
        elif isinstance(error, commands.NotOwner) or isinstance(error, commands.MissingPermissions):
            await ctx.reply(embed = Embed(description = "You do not have the permission to use this command!", color = Color.red()))
        
        elif isinstance(error, commands.BadUnionArgument):
            await ctx.reply(embed = Embed(description = "Error: conversion failed, please check the input provided.", color = Color.red()))
            
        elif isinstance(error, commands.UserInputError):
            await ctx.reply(embed = Embed(description = f"Input error: {error}", color = Color.red()))
            
        elif isinstance(error, commands.UserNotFound):
            await ctx.reply(embed = Embed(description = "Error: User not found", color = Color.red()))
		
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(embed = Embed(description = f"{error}", color = Color.red()))
        
        else:
            user.send(str(error))

    @staticmethod
    async def app_command_error_handler(interaction: 'Interaction', error: 'AppCommandError'):
        if isinstance(error, CheckFailure):
            await interaction.response.send_message('You don\'t have the permission to use this command!', ephemeral=True)
        else:
            user = interaction.client.get_user(586088176037265408)
            if isinstance(error, CommandInvokeError):
                error = error.original
            await interaction.response.send_message("An unexpected error occurred!", ephemeral = True)
            await user.send(str(error))

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))