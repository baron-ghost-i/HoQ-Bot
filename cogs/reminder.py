import discord, datetime, json
from discord.ext import (
commands,
tasks
)

class Reminder(commands.Cog):
	'''Creates a reminder command'''
	def __init__(self, bot):
		self.bot = bot
		self.reminder.start()
	
	@commands.command(aliases = ("reminder", "remind", "rem"))
	async def remindme(self, ctx, *args):
		'''Creates a reminder'''
		days, hrs, mins, sec = 0, 0, 0, 0
		args = list(args)
		for j in range(0, 60):
			for i in args:
				if f"{j}h" in i:
					hrs = int(args.pop(args.index(i)).replace("h", ""))
				if f"{j}m" in i:
					mins = int(args.pop(args.index(i)).replace("m", ""))
				if f"{j}s" in i:
					sec = int(args.pop(args.index(i)).replace("s", ""))
				if f"{j}d" in i:
					days = int(args.pop(args.index(i)).replace("d", ""))
			
		l = list(args)
		st = " ".join(l)

		embd = discord.Embed(description = f"Ok, will remind you in **{days}** days, **{hrs}** hr, **{mins}** min, **{sec}** s", color = 0xFFD700, timestamp = datetime.datetime.now(datetime.timezone.utc))
		embd.set_author(name = "{}".format(ctx.author), icon_url = "{}".format(ctx.author.avatar.url))

		await ctx.channel.send(embed = embd)

		t = sec + 60*mins + 3600*hrs + 86420*days
		tstr = f"{days} days, {hrs} hours, {mins} minutes and {sec} seconds"
		reptime = round(ctx.message.created_at.timestamp() + t)
		remdict = {"id": f"{ctx.author.id}", "time": f"{reptime}", "message": f"{st}", "delta": tstr}

		with open("data/reminders.json", "r") as reminder:
			l = json.loads(reminder.read())
		l.append(remdict)

		with open("data/reminders.json", "w") as reminder:
			reminder.write(json.dumps(l, indent = 2))

	@tasks.loop(seconds = 1.0)
	async def reminder(self):
		time_ = round(datetime.datetime.now().timestamp())
		with open("data/reminders.json", "r") as rem:
			lis = json.loads(rem.read())
		timestamps = [i["time"] for i in lis]
		if str(time_) in timestamps:
			remdict = lis.pop(timestamps.index(str(time_)))
			embd2 = discord.Embed(description = "Reminder: {}".format(remdict["message"]), color = 0xFFD700, timestamp = datetime.datetime.now(datetime.timezone.utc))
			user = self.bot.get_user(int(remdict["id"]))
			embd2.set_footer(text = "Set timer {} ago".format(remdict["delta"]))
			await user.send(embed = embd2)
			with open("data/reminders.json", "w+") as rem:
				rem.write(json.dumps(lis, indent = 2))


def setup(bot):
	bot.add_cog(Reminder(bot))