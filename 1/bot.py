from Piscord import *
from SAPAS import *

bot = Bot("Token")

@bot.event("on_ready")
def ready(ready):
	print(f"Bot {ready.name} Connected !")

@bot.event
def on_message(message):
	content = message.content.split()
	if len(content):
		if content[0]=="!avatar":
			if len(message.mentions)<1:
				user=message.author
			else:
				user=message.mentions[0]

			if user.avatar:
				embed = Embed({})
				embed.color = 3375070
				embed.title = f"{user.name}'s avatar"
				embed.image = Embed_Image({})
				embed.image.url = str(user.avatar)
				bot.send_message(message.channel_id,embed=embed.to_json())
			else:
				bot.send_message(message.channel_id,content="Aucun avatar")
	if message.content == "Ping !":
		channel = bot.get_channel(message.channel_id)
		invite = channel.create_invite()
		channel.send(content=f"Pong ! {message.author.mention} \n Invite : {invite}")

@bot.event
def reaction_add(reaction):
	reaction.get_message().add_reaction(reaction.emoji.name)

bot.start()
