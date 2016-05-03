import requests
import re
import pprint
from bs4 import BeautifulSoup

debug = True

def log(my_string):
    "Ensure that errors are propagated to the user"
    print my_string

def debug_print(my_string):
    "When debugging, print this out"
    if debug:
        print my_string

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
        possible_names = html.find_all(class_='team-name')
        if possible_names != []:
            #Use the first name
            country_name = possible_names[0].get_text()
        else:
            #No names were found
            country_name = "INVALIDCOUNTRY"
            log("WARNING: In finding teams, we could not establish a team name. The html is as follows: " + html.prettify())

        #Add the team's webpage to the team dictionary under link
        team_dictionary[country_name]= {'link' : (html['href'])}
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

def get_cup_match_data(base, extension):
    "For the given world cup, get match data"
    #Request page
    page = requests.get(base + extension)
    #Parse html
    soup = BeautifulSoup(page.content, 'html.parser')
    #Make regex to find match data
    #regex = re.compile("result")
    #Find links that match the regex
    results = soup.find_all("div",class_="mu result")
    links = []
    #For every resulting div, find the link
    for result in results:
        debug_print(result.prettify())
        link = result.find("a")['href']
        links.append(link)
    debug_print(links)
    return links

#Main section, do this:
base = "http://www.fifa.com"
teams_website = base + '/fifa-tournaments/teams/search.html'
team_dictionary = get_teams(teams_website)
#get_all_teams_data(base,team_dictionary)
debug_print("--------------------------------")
get_cup_match_data(base,"/worldcup/archive/uruguay1930/matches/index.html")


#Debug subset
#country_names = {'Brazil'}
#test_dict = { key:value for key,value in team_dictionary.items() if key in country_names }
#get_all_teams_data(base, test_dict)
#if debug:
#    pretty_print_dict(test_dict)

#get_cup_match_data(base,"/worldcup/archive/uruguay1930/matches/index.html")

#-------------------------------------------
#TODONE: General stats per team
#        Appearances, Matches Played, Goals Scored, and Average Goals

#TODO: Get list of editions 
#http://www.fifa.com/fifa-tournaments/archive/worldcup/index.html

#TODO: Specific edition stats per team
#http://www.fifa.com/fifa-tournaments/teams/association=USA/index.html
# Edition, Placement, Matches Played, Wins, Draws, Losses, Goals Scored, Goals Against, Goals Scored Average, Goals Against Average

#TODO: General stats per edition
#http://www.fifa.com/worldcup/archive/uruguay1930/statistics/index.html
#Matches Played, Goals Scored, Average Card per Match, Goals per Match 

#TODO: Matches per edition
#http://www.fifa.com/worldcup/archive/uruguay1930/matches/index.html
#Group Number, Date, Time, Venue, Stadium, WinningTeamName, LosingTeamName, WinningTeamScore, LosingTeamScore

#TODO: Players????? oh dear
