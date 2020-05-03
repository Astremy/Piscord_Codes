from Piscord import *

bot = Bot("Token")

@bot.event("on_ready")
def ready(ready):
	print(f"Bot {ready.name} Connected !")

@bot.event
def on_message(message):
	content = message.content.split()
	if len(content):
		if content[0] == "!invite_info":
			if len(message.mentions)<1:
				user=message.author
			else:
				user=message.mentions[0]
			total = 0
			nb_invites = 0
			invites = bot.get_guild(message.guild_id).get_invites()
			for invite in invites:
				if invite.inviter.id == user.id:
					nb_invites +=1
					total += invite.uses
			channel = bot.get_channel(message.channel_id)
			embed = Embed({})
			embed.color = 3375070
			embed.title = f"Information sur {user}"
			embed.description = f"Nombre d'invitations différentes : {nb_invites}\nUtilisations totales : {total}"
			embed.thumbnail.url = user.avatar
			bot.send_message(message.channel_id,embed=embed.to_json())
			
bot.start()