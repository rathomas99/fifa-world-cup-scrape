import requests
import re
import pprint
from bs4 import BeautifulSoup
import load

debug = False
db = None

def log(my_string):
	"Ensure that errors are propagated to the user"
	print(my_string)

def debug_print(my_string):
	"When debugging, print this out"
	if debug:
		print(my_string)

def pretty_print_dict(my_dict):
	"Pretty print the dictionary"
	pp = pprint.PrettyPrinter(depth=3)
	pp.pprint(my_dict)

def get_teams(website):
	"Get the links of the teams"
	#Get the website html
	page = requests.get(website)
	#Parse the website html
	soup = BeautifulSoup(page.content, 'html.parser')
	#Make a regex that will find the links that go to team-specific pages
	regex = re.compile('team')
	#Execute that regex (look for links matching the regex)
	all_teams_html = soup.find_all(href=regex)
	#Initialize the team dictionary
	team_dictionary = {}
	#For each team, look at its html and extract information
	for html in all_teams_html:
		#Acquire the name of the country from its html
		#Use the first name
		name = html.find(class_='team-name')
		if name != None:
			country_name = name.get_text()
		else:
			#No names were found
			country_name = "INVALIDCOUNTRY"
			log("WARNING: In finding teams, we could not establish a team name. The html is as follows: " + html.prettify())
		flag = html.find("img", class_="flag")
		if flag != None:
			flag = flag["src"]
		#Add the team's webpage to the team dictionary under link
		team_dictionary[country_name]= {'link' : (html['href']), 'flag' : flag}
	#Return the team dictionary	
	return team_dictionary

def get_team_data(base, team):
	"For the given team, acquire general world cup data"
	#Find the team's webpage 
	link = team["link"]
	#Get the website html
	page = requests.get(base + link)
	#Parse the website html
	soup = BeautifulSoup(page.content, 'html.parser')
	#Find all statistical data and appropriate name
	stats_names = soup.find_all(class_="label-name")
	team_stats = soup.find_all(class_="label-data")
	#For every stat, put the stats in this team's part of the dictionary
	for stat_name_html,value_html in zip(stats_names,team_stats):
		stat_name = stat_name_html.get_text()
		value = value_html.get_text()
		debug_print(stat_name)
		debug_print(value)
		if stat_name != " ":
			#add value to the list of values at team[stat_name]
			team.setdefault(stat_name, []).append(value)
	debug_print("-------------")

def get_all_teams_data(base, teams_dict):
	"For the given teams, acquire general world cup data for each"
	for team in teams_dict:
		get_team_data(base,teams_dict[team])

def get_all_match_data(base, extension):
	debug_print("Get cups")
	list_of_link_to_cup_matches,cups = get_cups(base, extension)
	load_cups(cups)
	debug_print("Go through cups")
	for link in list_of_link_to_cup_matches:
		debug_print(link)
		matches = get_cup_match_links(base,link)
		debug_print("done getting matches")
		for match in matches:
			debug_print(match)
			match_data = get_match_data(base, match)
			load_match(match_data)
			debug_print("done getting match data")
			
def get_cups(base,extension):
	"Find the links to the matches page of each world cup edition"
	#Request page - http://www.fifa.com/fifa-tournaments/archive/worldcup/index.html
	page = requests.get(base + extension)
	#Parse html
	soup = BeautifulSoup(page.content, 'html.parser')
	#Find li's that match "comp-item"
	results = soup.find_all("li",class_="comp-item")
	cups = {}
	links = []
	#For every resulting div, find the link
	for result in results:
		#debug_print(result.prettify())
		name = result.find("div", class_="comp-name").get_text().strip()
		#Example name: Brazil 2014
		year = str(name)[-4:]#last 4 characters of name is the year ex. 2014
		name = str(name)[:-5]#chop off the last 5 characters ex. ' 2014'
		link = result.find("a")['href']
		#Example link:
		#http://www.fifa.com/worldcup/archive/brazil2014/index.html
		#Desired answer:
		#http://www.fifa.com/worldcup/archive/brazil2014/matches/index.html
		link = link.replace("index.html","matches/index.html")
		links.append(link)
		cups[name] = {"link":link, "year":year}
	debug_print(links)
	return links,cups		

	
def start_load():
	global db
	db = load.openDB()
	return db
	
def load_cups(cups):
	global db
	for cup in cups:
		name = cup
		year = cups[cup]["year"]
		load.insert_cup(db,name,year)
	if debug:
		load.retrieve_cups(db)
		
def load_match(match_data):
	global db
	match_id = match_data["match_id"]
	cup_year = match_data["cup_year"]
	home_team = match_data["home_team_id"]
	away_team = match_data["away_team_id"]
	load.insert_match(db,match_id,cup_year,home_team,away_team)
	
def get_cup_match_links(base, extension):
	"For the given world cup, get link to match webpages"
	#Request page 
	#Example page - "http://www.fifa.com/worldcup/archive/uruguay1930/matches/index.html"
	page = requests.get(base + extension)
	#Parse html
	soup = BeautifulSoup(page.content, 'html.parser')
	#Find divs that match "mu result"
	results = soup.find_all("div",class_="mu result")
	links = []
	#For every resulting div, find the link
	for result in results:
		#debug_print(result.prettify())
		link = result.find("a")['href']
		links.append(link)
	debug_print(links)
	return links

def get_match_data(base,extension):
	"For the given match, get data"
	#Request page 
	#Example page- "http://www.fifa.com/worldcup/matches/round=201/match=1093/report.html"
	page = requests.get(base + extension)
	#Parse html
	soup = BeautifulSoup(page.content, 'html.parser')
	
	#Set up match dictionary
	match = {}
	#Find the cup year
	cup_year = soup.find("title").get_text()
	cup_year = cup_year[:4]
	
	#debug_print(cup_year)
	
	#Find first div that match "mh result"
	result = soup.find("div",class_="mh result")
	#Find the match information
	if result != None:
		#debug_print(result.prettify())
		#match id
		match_id = result["data-id"]
		#stadium and venue
		stadium = result.find("span",class_="mh-i-stadium").get_text()
		venue = result.find("span",class_="mh-i-venue").get_text()
		#time
		given_datetime = result.find("div",class_="mh-i-datetime").get_text()
		day_month_numbers = result.find("div",class_="s-score s-date-HHmm")["data-daymonthutc"]
		#Round = Groups/Semifinals/Finals
		round = result.find("div",class_="mh-i-round").get_text()
		#Status = Full-time
		status = result.find("div",class_="s-status").get_text()
		#Home and away team ids
		home_team_id = result.find("div",class_="t home")["data-team-id"]
		away_team_id = result.find("div",class_="t away")["data-team-id"]
		#Home and away scores
		score = result.find("span",class_="s-scoreText").get_text()
		home_score, away_score = score.split("-")
		#Reason of win
		reason_win = result.find("span",class_="text-reasonwin").get_text()
		
		home_scorer_ids, away_scorer_ids = get_scorers(result)
		
		match = {"match_id":match_id, "home_team_id": home_team_id, "away_team_id": away_team_id, "home_score":home_score, "away_score": away_score}
		match["stadium"] = stadium
		match["venue"] = venue
		match["round"] = round
		match["status"] = status 
		match["cup_year"] = cup_year
		
		if reason_win != "" and reason_win != " ":
			match["reason_win"] = reason_win
		#Currently the date is formatted as monthmonth/dayday
		match["date"] = str(day_month_numbers[2:4]) + "/" + str(day_month_numbers[0:2])
		#TODO GET YOUR OWN DAMN YEAR
		debug_print("MATCH")
		debug_print(pretty_print_dict(match))
		debug_print("HOME SCORERS")
		debug_print(home_scorer_ids)
		debug_print("AWAY SCORERS")
		debug_print(away_scorer_ids)
		
	report = soup.find("div", class_="match-report")
	get_report_innards(report)
	return match

	
def get_scorers(result):
	"For a match, find players who scored goals"
	#TODO Find type of goal
	#TODO Find time of goal
	#TODO Find number of goals
	if result != None:
		#Find player ids of the players that scored for the home team
		home_scorers_html = result.find("div",class_="t-scorer home")
		home_scorers = home_scorers_html.find_all("li",class_="mh-scorer")
		home_scorer_ids = []
		for home_scorer in home_scorers:
			id = home_scorer.find("span").find("div")["data-player-id"]
			home_scorer_ids.append(id)
			#debug_print(id)
		#Find player ids of the players that scored for the away team
		away_scorers_html = result.find("div",class_="t-scorer away")
		away_scorers = away_scorers_html.find_all("li",class_="mh-scorer")
		away_scorer_ids = []
		for away_scorer in away_scorers:
			id = away_scorer.find("span").find("div")["data-player-id"]
			away_scorer_ids.append(id)
			#debug_print(id)
		return home_scorer_ids, away_scorer_ids
	
def get_report_innards(report):
	#TODO GET ATTENDANCE
	#TODO GET YEAR
	#Set up dictionary to be used for officials
	officials = {}
	if report != None:
		#Find referees table
		officials_html = report.find("div",class_="match-official")
		officials_row_data = officials_html.find_all("td")
		for official in officials_row_data:
			kind_of_referee = official.find("div",class_="people-kind-name").get_text()
			name_of_referee = official.find("div",class_="people-name").get_text()
			#Example Name of Referee: BALWAY Thomas (FRA)
			name_of_referee,country_of_referee = name_of_referee.split(" (")
			country_of_referee = country_of_referee[:-1]
			#debug_print(kind_of_referee + "///" + name_of_referee + "///" + country_of_referee)
			officials[kind_of_referee] = {"name":name_of_referee, "country" : country_of_referee}
		
		home_lineup = []
		away_lineup = []
		lineup = report.find("div",class_="lineup").find("table",class_="table fielded")
		#debug_print(lineup.prettify())
		subs = report.find("div",class_="lineup").find("table",class_="table substitutes")
		
		home_rows = lineup.find_all("td",class_="home")
		for row in home_rows:
			home_id = row.find("div")["data-player-id"]
			home_lineup.append(home_id)
	
		away_rows = lineup.find_all("td",class_="away")
		for row in away_rows:
			away_id = row.find("div")["data-player-id"]
			away_lineup.append(away_id)
			
		debug_print("MATCH REPORT")
		debug_print(home_lineup)
		debug_print(away_lineup)
		debug_print(pretty_print_dict(officials))		
	return officials

	
def main():
	base = "http://www.fifa.com"
	start_load()
	get_all_match_data(base,"/fifa-tournaments/archive/worldcup/index.html")
	
	#links, cups = get_cups(base,"/fifa-tournaments/archive/worldcup/index.html")
	#debug_print(pretty_print_dict(cups))
	#load_cups(start_load(),cups)
	#get_match_data(base,"/worldcup/matches/round=201/match=1093/report.html")
	
	#team_dictionary = get_teams(base + '/fifa-tournaments/teams/search.html')
	#debug_print(pretty_print_dict(team_dictionary))
	
#Main section, do this:
main()

#teams_website = base + '/fifa-tournaments/teams/search.html'
#team_dictionary = get_teams(teams_website)
#get_all_teams_data(base,team_dictionary)

#debug_print("--------------------------------")

#get_cup_match_links(base,"/worldcup/archive/uruguay1930/matches/index.html")
#get_match_data(base,"/worldcup/matches/round=201/match=1093/index.html#")
#get_match_data(base,"/worldcup/matches/round=201/match=1093/report.html","1930")


#get_all_match_data(base,"/fifa-tournaments/archive/worldcup/index.html")

#Debug subset
#country_names = {'Brazil'}
#test_dict = { key:value for key,value in team_dictionary.items() if key in country_names }
#get_all_teams_data(base, test_dict)
#if debug:
#	pretty_print_dict(test_dict)

#get_cup_match_data(base,"/worldcup/archive/uruguay1930/matches/index.html")

#-------------------------------------------
#TODONE: General stats per team
#		Appearances, Matches Played, Goals Scored, and Average Goals

#TODO: Get list of editions 
#http://www.fifa.com/fifa-tournaments/archive/worldcup/index.html

#TODO: Specific edition stats per team
#http://www.fifa.com/fifa-tournaments/teams/association=USA/index.html
# Edition, Placement, Matches Played, Wins, Draws, Losses, Goals Scored, Goals Against, Goals Scored Average, Goals Against Average

#TODO: General stats per edition
#http://www.fifa.com/worldcup/archive/uruguay1930/statistics/index.html
#Matches Played, Goals Scored, Average Card per Match, Goals per Match 

#TODONE: Matches per edition
#http://www.fifa.com/worldcup/archive/uruguay1930/matches/index.html
#Group Number, Date, Time, Venue, Stadium, WinningTeamName, LosingTeamName, WinningTeamScore, LosingTeamScore

#TODO: Players????? oh dear
