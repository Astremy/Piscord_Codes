from Piscord import *
from SAPAS import *
import os
import json

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

quiz = [
	["Quel est votre age ?",["🚸","👦","👨‍🎓","👨‍💼"],["- 13 ans", "13 - 18 ans", "18 - 25 ans","+ 25 ans"]],
	["Comment qualifieriez-vous votre niveau en programmation ?",["⬇️","↘️","➡️","↗️","⬆️"],["Très bas", "Assez Bas", "Moyen", "Assez élevé", "Très élevé"]],
	["Quel langage utiliserez-vous ?",["🐍","☕","🇨","🌀","❓"],["Python", "Java", "C / C++ / C#", "Javascript", "Autre"]],
]

with open("participants.json","r") as file:
	people = json.loads(file.read())

bot = Bot("Token",api_sleep=0.1)

toggle = [True]

@bot.event
def on_message(message):
	content = message.content.split()
	if content:
		if content[0] == "!send" and message.channel.id == "712675691002593311":
			verif_chann = bot.get_element(message.guild.channels,"712675084086542384")
			embed = Embed()
			embed.description = " ".join(content[1:])
			embed.author.icon_url = message.author.avatar
			embed.author.name = message.author.name
			verif_chann.send(embed = embed.to_json())
			message.delete()
		if content[0] == "!register" and message.channel.id == "712719147985010798":
			if toggle[0]:
				message.delete()
				people[message.author.id] = [0,[],[message.author.name,message.author.avatar],1]
				embed = Embed()
				embed.title = "Inscription au Concours"
				embed.description = "Pour vous inscrire au concours, veuillez répondre à un questionnaire, pour le commencer, cliquez sur la réaction sous ce message"
				mess = message.author.dm.send(embed=embed.to_json())
				mess.add_reaction("🌟")
			else:
				message.channel.send("Les inscriptions sont fermées")
		if message.author.id == "263331548542009348":
			if content[0] == "!toggle":
				toggle[0] = not toggle[0]
				message.channel.send(f"Toggle : {toggle[0]}")
			if content[0] == "!reload":
				with open("participants.json","r") as file:
					p = json.loads(file.read())
					people.clear()
					for a,b in p.items():
						people[a] = b
				message.channel.send("Reload Complete !")

@bot.event
def reaction_add(reaction):
	if reaction.user_id == bot.user.id:
		return
	channel = reaction.message.channel
	if toggle[0]:
		if channel and channel.type == 1:
			if reaction.user_id in people:
				user = people[reaction.user_id]
				if user[0] <= len(quiz):
					if user[0]:
						question = quiz[user[0]-1]
						if not reaction.emoji.react in question[1]:
							return
						user[1].append(question[2][question[1].index(reaction.emoji.react)])
					user[0]+=1
					if user[0] > len(quiz):
						embed = Embed()
						guild = bot.get_element(bot.guilds,"712674290125766758")
						candid = guild.get_member(reaction.user_id)
						embed.title = candid.name
						embed.thumbnail.url = candid.avatar
						for i in range(len(user[1])):
							embed.add_field(name=quiz[i][0],value=user[1][i])
						bot.get_element(guild.channels,"712744306074714162").send(embed = embed.to_json())
						candid.add_role(bot.get_element(guild.roles,"712779243058102379"))
						with open("participants.json","w") as file:
							file.write(json.dumps(people, indent=4))
						return channel.send("Le formulaire a bien été envoyé, merci !")
					question = quiz[user[0]-1]
					embed = Embed()
					embed.title = f"Question {user[0]}"
					embed.description = "\n".join([question[0],*(f"{a} : {b}" for a,b in zip(question[1],question[2]))])
					mess = channel.send(embed = embed.to_json())
					for emoji in question[1]:
						mess.add_reaction(emoji)

bot.start()

site = Server("0.0.0.0",80)

auth = OAuth(bot,"Secret","http://localhost/connect","identify")

@site.path("/")
def liste(user):
	juge = ""
	textconnect = "connecter"
	lienconnect = "/connect"
	if "token" in user.cookies:
		textconnect = "déconnecter"
		lienconnect = "/disconnect"
		try:
			user = auth.get_user(user.cookies["token"])
			guild = bot.get_element(bot.guilds,"712674290125766758")
			member = guild.get_member(user.id)
			if "712677330115625071" in member.roles:
				juge = "<a class='text-sm text-red-700' href='/remove/{}'>Remove</a>"
		except:...
	s = []
	for user_id,member in people.items():
		if member[0] > len(quiz):
			juge_html = ""
			color = "red-400"
			if member[3]:
				juge_html = juge.format(user_id)
				color = "white"
			s.append(template("user.html", avatar = member[2][1], name = member[2][0], language = member[1][2],juge = juge_html, color = color))
	users = ""
	for i in range(len(s)):
		if not i%3:
			users += "<div class='flex justify-around'>"
		users += s[i]
		if not (i+1)%3:
			users += "</div>"
	if len(s)%3:
		users += "</div>"
	return template("list.html",users = users, textconnect = textconnect, lienconnect = lienconnect)

@site.path("/connect")
def connect(user):
	if "code" in user.request.form:
		token = auth.get_token(user.request.form["code"])
		user.set_cookie("token",json.dumps(token))
		return redirect(user,"/")
	elif "error" in user.request.form:
		return redirect(user,"/")
	else:
		return redirect(user,auth.get_url())

@site.path("/disconnect")
def disconnect(user):
	user.delete_cookie("token")
	return redirect(user,"/")

@site.path("/remove/{var}")
@need_cookies("token")
def remove(user,var):
	try:
		user_bot = auth.get_user(user.cookies["token"])
		guild = bot.get_element(bot.guilds,"712674290125766758")
		member = guild.get_member(user_bot.id)
		if "712677330115625071" in member.roles:
			if var in people:
				m = guild.get_member(var)
				m.remove_role(bot.get_element(guild.roles,"712779243058102379"))
				m.add_role(bot.get_element(guild.roles,"713823395095248898"))
				people[var][3] = 0
				with open("participants.json","w") as file:
					file.write(json.dumps(people, indent=4))
	except:...
	return redirect(user,"/")

site.start()
