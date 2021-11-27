import discord
import json

class Slashcommands:
    '''Compiles all slashcommands in a single class'''
	
    def __init__(self, bot, interaction):
	    self.bot = bot
	    self.interaction: discord.Interaction = interaction
	    self.data: dict = {}
	    try:
	    	for i in self.interaction.data["options"]:
			    self.data[i["name"]] = i["value"]
	    except:
		    pass
			
    def id(self, id: int):
	    if any([id == 850039242481991700, id == 808257138882641960, id == 839939906558361627, id == 786520972064587786]):
		    return 612234021388156938
	    return id

    async def ping(self):
	    await self.interaction.response.send_message(f"Ping: {round(self.bot.latency*1000)} ms")

    async def addresponse(self):
	    if any(["__" in self.data["response"], "lambda" in self.data["response"]]):
		    await self.interaction.response.send_message("Cannot add that autoresponse!", ephemeral = True)
		    return
			
	    if not self.interaction.user.guild_permissions.manage_messages:
		    await self.interaction.response.send_message("You do not have the permission to use this command", ephemeral = True)
		    return

	    with open("data/autoresponses.json") as fob:
		    data = json.loads(fob.read())
			
	    id_ = self.id(self.interaction.guild_id)
	    self.data["trigger"] = self.data["trigger"].lower()
	    wildcard = self.data.pop("wildcard")
	    type1, type2 = "normal", "wildcard"
	    nonepair = {"trigger": None, "response": None}
		
	    if wildcard:
		    type1, type2 = type2, type1

	    if str(id_) not in data:
		    data[str(id_)] = {type1: [self.data], type2: [nonepair]}
	    else:
		    data[str(id_)][type1].append(self.data)
		
	    if nonepair in data[str(id_)][type1] and len(data[str(id_)][type1]) > 1:
		    data[str(id_)][type1].remove(nonepair)
		
	    with open("data/autoresponses.json", "w") as fob:
		    json.dump(data, fob, indent = 2)
	    await self.interaction.response.send_message("Autoresponse successfully added!")