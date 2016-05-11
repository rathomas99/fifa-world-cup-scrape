from bs4 import BeautifulSoup
import requests
import load
from fake_useragent import UserAgent

ua = UserAgent()

db = load.openDB()
base = "http://www.fifa.com/fifa-tournaments/players-coaches/people"
#rest = "/library/_people_detail.htmx"
rest = "/index.html"
#"http://www.fifa.com/fifa-tournaments/players-coaches/people=46364/library/_people_detail.htmx"
#http://www.fifa.com/fifa-tournaments/players-coaches/people=207528/index.html

def log(string):
	print(string)

def debug_print(string):
	print(string)
	
numbers = range(1,999999)
#numbers = [30,36,103,107,109,310,174456]
#numbers = [174456]
for number in numbers:
	try:
		player_link= base + str(number) + rest
		#Request page
		headers = {'User-Agent': ua.random}
		page = requests.get(base + player_link, headers=headers)
		#Parse html
		soup = BeautifulSoup(page.content, 'html.parser')
		screaming = False
		title = soup.find("title")
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