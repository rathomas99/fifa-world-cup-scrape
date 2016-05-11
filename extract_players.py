from bs4 import BeautifulSoup
import requests
import load

base = "http://www.fifa.com/fifa-tournaments/players-coaches/people"
rest = "/library/_people_detail.htmx"
#"http://www.fifa.com/fifa-tournaments/players-coaches/people=46364/library/_people_detail.htmx"

def log(string):
	print(string)

def debug_print(string):
	print(string)
	
#numbers = range(10000,999999)
numbers = [30,36,103,107,109,310,174456]
for number in numbers:
	try:
		player_link= base + str(number) + rest
		#Request page
		page = requests.get(base + player_link)
		#Parse html
		soup = BeautifulSoup(page.content, 'html.parser')
		screaming = False
		title = soup.find("title")
		if "FIFA.com" in title:
			log("WARNING: You hit the unfound page page " + str(number))
		else:
			debug_print(title)
			try:
				guesses = soup.find_all("div")
				player_id = "-1"
				for guess in guesses:
					#log(str(guess.prettify("latin-1")))
					try:
						player_id = guess["data-player-id"]
						debug_print("found it")
					except KeyError as e:
						if screaming:
							print("sigh")
				
				debug_print("player id " + player_id)
				
				root_birth = soup.find("div",class_="people-dob")
				if not (root_birth):
					log("WARNING: There isn't a birthday listed for this player")
				guesses = soup.find_all("span",class_="data")
				birthday = "0000-00-00"
				if [] == guesses:
					log("WARNING: THERE ARE NO GUESSES FOR BIRTHDAY WHYYYYYY")
				for guess in guesses:
					#log(str(guess.prettify("latin-1")))
					birthday = guess.get_text()
				
				load.insert_player(db,player_id,player_name,birthday)
			except AttributeError as e:
				log("ERROR: Load uninserted player - id and birthday damn it " + str(e))
	except Exception as e:
		log("ERROR: " + str(e))