import requests
import re
import pprint
from bs4 import BeautifulSoup
import load

debug = True
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
	#if debug:
		#pretty_print_dict(team_dictionary)
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
		#Get rid of the trademark symbol
		if '\u2122' in value:
			value = value.replace('\u2122',"")
		#debug_print(stat_name)
		#debug_print(value)
		if stat_name != " ":
			#add value to the list of values at team[stat_name]
			team.setdefault(stat_name, []).append(value)
	#Let's assume we only want the first piece of data for each category
	for thing in team:
		if thing != "flag" and thing  != "link":
			team[thing] = team[thing][0]
	if debug:
		pretty_print_dict(team)
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
			debug_print("done getting match data")
			load_match(match_data)
			load_goals(match_data)
	return cups
			
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
		cups[year] = {"link":link, "name":name, "year":year}
	debug_print(links)
	return links,cups		

def get_cup_membership(base, cup, team_dictionary):
	"Find what teams are participating in a cup"
	link = cup["link"]
	#link should be of the form http://www.fifa.com/worldcup/archive/brazil2014/matches/index.html
	#change it to http://www.fifa.com/worldcup/archive/brazil2014/teams/index.html
	link = link.replace("matches","teams")
	
	cup_year = cup["year"]
	
	page = requests.get(base + link)
	#Parse html
	soup = BeautifulSoup(page.content, 'html.parser')
	
	cup_team_links_html = soup.find_all("a",class_="team")
	for link_html in cup_team_links_html:
		#Example link: http://www.fifa.com/worldcup/archive/brazil2014/teams/team=43976/index.html
		link = link_html["href"]
		name = link_html.find(class_='team-name').get_text()
		team_id = (link.split("teams/team=")[1]).split("/index.html")[0]
		
		#debug_print(link)
		#debug_print(team_id)
		#debug_print(name)
		#debug_print(cup_year)		
		
		if name in team_dictionary:
			team_dictionary[name]["team_id"] = team_id		
			team_dictionary[name].setdefault("participations", []).append(cup_year)
			team_dictionary[name]["members"] = {}
			get_team_membership(base, cup_year, team_id, link, team_dictionary[name]["members"])
			

def  get_team_membership(base, cup_year, team_id, link, members_dictionary):
	"For the given cup and team webpage, find team members who participated"
	#Example link: http://www.fifa.com/worldcup/archive/uruguay1930/teams/team=43924/players.html
	#"http://www.fifa.com/worldcup/archive/edition=1930/library/teams/team=43924/_players/_players_list.html"
	
	#link.replace("index.html","players.html")
	
	link = "/worldcup/archive/edition=" + cup_year + "/library/teams/team=" + team_id + "/_players/_players_list.html"
	
	page = requests.get(base + link)
	#Parse html
	soup = BeautifulSoup(page.content, 'html.parser')
	
	members_dictionary[cup_year] = []
	debug_print("Acquiring team members for cup " + cup_year)
	player_list_html = soup.find("div", class_="p-list clearfix")
	#debug_print(player_list_html.prettify())
	player_list = player_list_html.find_all("div", class_="p p-i-no")
	for player in player_list:
		#debug_print("-=-=--=-=-=-=-=-=-=-=-=-=-=-")
		player_id = player["data-player-id"]
		player_name = player["data-player-name"]
		player_link = player.find("a")
		if player_link != None:
			player_link = player_link["href"]
		player_position = player.find("span", class_="p-i-fieldpos").get_text()
		player_birthdate = player.find("span", class_="data")
		if player_birthdate:
			player_birthdate_YYYY_MM_DD = player_birthdate["data-birthdate"]
			player_birthdate_english = player_birthdate.get_text()
		
		player_dict = {"player_id" : player_id, "player_name" : player_name, "player_link" : player_link, "player_position" : player_position}
		members_dictionary[cup_year].append(player_dict)
		#debug_print(player_id)
		#if debug:
			#pretty_print_dict(player_dict)
	
	
def start_load():
	global db
	db = load.openDB()
	return db
	
def load_cups(cups):
	global db
	for cup in cups:
		name = cups[cup]["name"]
		year = cups[cup]["year"]
		load.insert_cup(db,name,year)
	#if debug:
		#load.retrieve_cups(db)
	
def load_teams(team_dictionary):
	global db
	for team in team_dictionary:
		if 'team_id' in team_dictionary[team]:
			team_id = team_dictionary[team]["team_id"]
			name = team
			flag = team_dictionary[team]["flag"]
			load.insert_team(db,team_id,name,flag)
			debug_print("===============")
			debug_print(name)
			debug_print(team_id)
			debug_print(flag)
			
def load_team_cup_memberships(team_dictionary):
	global db
	debug_print("HEREHEHREHRKEJRKLEJR")
	for team in team_dictionary:
		debug_print("======------======")
		pretty_print_dict(team_dictionary[team])
		if 'team_id' in team_dictionary[team]:
			team_id = team_dictionary[team]["team_id"]
			debug_print(team)
			participations = team_dictionary[team]["participations"]
			for cup_year in participations:
				#rank = participations["cup_year"]["rank"]
				rank = -1
				#TODO GET RANK
				debug_print(cup_year)
				load.insert_team_cup_membership(db,str(team_id),str(cup_year),str(rank))
				
def load_match(match_data):
	global db
	if "match_id" in match_data:
		match_id = match_data["match_id"]
		cup_year = match_data["cup_year"]
		home_team = match_data["home_team_id"]
		away_team = match_data["away_team_id"]
		home_score = match_data["home_score"]
		away_score = match_data["away_score"]
		stadium = match_data["stadium"] 
		venue =	match_data["venue"]
		round =	match_data["round"]
		month = match_data["month"]
		day = match_data["day"]
		load.insert_match(db,match_id,cup_year,home_team,away_team,home_score,away_score,venue,stadium,month,day)
	
def load_goals(match):
	global db
	if "match_id" in match:
		match_id = match["match_id"]
		if "goals" in match:
			goals = match["goals"]
			for time in goals:
				goal = goals[time]
				type = goal["type"]
				player_id = goal["player_id"]
				team_id = goal["team_id"]
				load.insert_goal(db,time,player_id,match_id,type,team_id)
	
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
		
		goals = get_scorers(result,home_team_id,away_team_id)
		
		match = {"match_id":match_id, "home_team_id": home_team_id, "away_team_id": away_team_id, "home_score":home_score, "away_score": away_score}
		match["stadium"] = stadium
		match["venue"] = venue
		match["round"] = round
		match["status"] = status 
		match["cup_year"] = cup_year
		
		if reason_win != "" and reason_win != " ":
			match["reason_win"] = reason_win
		
		#day_month_numbers is daydaymonthmonth
		match["month"] = str(day_month_numbers[2:4]) 
		match["day"] = str(day_month_numbers[0:2])
		
		#Put in scorers
		match["goals"] = goals
		
		debug_print("MATCH")
		if debug:
			pretty_print_dict(match)
		debug_print("GOALS")
		if debug:
			pretty_print_dict(goals)
		
	report = soup.find("div", class_="match-report")
	get_report_innards(report)
	return match
	
def get_scorers(result,home_team_id,away_team_id):
	"For a match, find players who scored goals"
	#TODO Find type of goal
	#TODO Find time of goal
	#TODO Find number of goals
	goals = {}
	if result != None:
		#Find player ids of the players that scored for the home team
		home_scorers_html = result.find("div",class_="t-scorer home")
		home_scorers = home_scorers_html.find_all("li",class_="mh-scorer")
		goals = for_loop_scorers(goals,home_team_id,home_scorers)
			
		#Find player ids of the players that scored for the away team
		away_scorers_html = result.find("div",class_="t-scorer away")
		away_scorers = away_scorers_html.find_all("li",class_="mh-scorer")
		goals = for_loop_scorers(goals,away_team_id,away_scorers)
		
		return goals
	
def for_loop_scorers(goals, specified_team_id,specified_scorers):
	"For a player, find goals and their type"
	for scorer in specified_scorers:
			player_id = scorer.find("span").find("div")["data-player-id"]
			goals_html = scorer.find_all("span", class_="ml-scorer-evmin")
			for goal_html in goals_html:
				goal_text = goal_html.find("span").get_text()
				debug_print(goal_text)
				#Only use the first two characters of the text
				minutes_since_start = goal_text[0:2]
				goals[minutes_since_start] = {}
				goals[minutes_since_start]["player_id"] = player_id
				goals[minutes_since_start]["team_id"] = specified_team_id
				if "PEN" in goal_text:
					debug_print("penalty goal")
					goals[minutes_since_start]["type"] = "Penalty"
				elif "OG" in goal_text:
					debug_print("own goal")
					goals[minutes_since_start]["type"] = "Self"
				else:
					goals[minutes_since_start]["type"] = "Regular"
	return goals
	
def get_report_innards(report):
	#TODO GET ATTENDANCE
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
		if debug:
			pretty_print_dict(officials)		
	return officials

def main():
	base = "http://www.fifa.com"
	start_load()
	
	#cups = get_all_match_data(base,"/fifa-tournaments/archive/worldcup/index.html")
	links, cups = get_cups(base,"/fifa-tournaments/archive/worldcup/index.html")
	#load_cups(cups)
	#debug_print(pretty_print_dict(cups))
	
	#-------------------
	
	team_dictionary = get_teams(base + '/fifa-tournaments/teams/search.html')
	#debug_print(pretty_print_dict(team_dictionary))
	country_names = {'Brazil'}#,'Qatar','USA', 'Japan'}
	test_dict = { key:value for key,value in team_dictionary.items() if key in country_names }
	
	get_all_teams_data(base, test_dict)
	pretty_print_dict(test_dict)
	test_cup_years = ['1930']#['2014','1930','1950']
	
	for cup in test_cup_years:
		get_cup_membership(base, cups[cup], team_dictionary)
	load_team_cup_memberships(test_dict)
	
	pretty_print_dict(test_dict['Brazil']['members']['1930'])

	#get_cup_membership(base,cups["2014"],test_dict)
	#pretty_print_dict(team_dictionary)
	#load_teams(team_dictionary)
	#get_match_data(base,"/worldcup/matches/round=201/match=1093/report.html")
	
	
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
