import requests
import pprint
from lxml import html
from lxml import etree
from lxml.html.clean import clean_html

def get_html_tree(url):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    return tree

def get_teams(base):
    "Get the names and links of the teams"
    #{'Brazil': {'link':'/fifa-tournaments/teams/association=BRA/index.html'}, 'Canada':{stuff}}
    
    #XPath of relevant stuff                                                                              
    # for the capitalized name, i think 
    # //*[@id="teamsBrowser"]/div[4]/div[1]/ul/li[1]/a/span
    # for the team link
    # //*[@id="teamsBrowser"]/div[4]/div[1]/ul/li[1]/a
    tree = get_html_tree(base + '/fifa-tournaments/teams/search.html')
    country_names = tree.xpath('//*[@id="teamsBrowser"]/div/div/ul/li/a/span/text()')
    #print country_names[0]
    links = tree.xpath('//*[@id="teamsBrowser"]/div/div/ul/li/a/@href')
    #print links[0]    
    #teams_dict = dict(zip(country_names,links))
    teams_dict = {}
    for country,link in zip(country_names,links):
        teams_dict[country] = {"link": link}
    #print teams_dict
    return teams_dict

def get_team_data(base, team):
    "For the given team, acquire general world cup data"
    #general, over all world cups
    # //*[@id="tournamentstats"]/div[2]/div/div/ul[1]/li[2]/div[2]/span
    #specific world cup editions
    # //*[@id="tournamentstats"]/div[2]/div/div/div[1]/div/table/tbody/tr[1]/td[1]
    link = team["link"]
    tree = get_html_tree(base + link)
    team_stats = tree.xpath('//*[@id="tournamentstats"]/div[2]/div/div/ul[@class="first"]/li/div[@class="label-data"]/span/text()')
    #stat_names = tree.xpath('//*[@id="tournamentstats"]/div[2]/div/div/ul[@class="first"]/li/@class')
    stats_names = tree.xpath('//*[@id="tournamentstats"]/div[2]/div/div/ul[@class="first"]/li/div[@class="label-name"]/text()')
    #print stats_names
    #print zip(stats_names,team_stats)
    if (u'FIFA World Cup\u2122' in team_stats):
        for stat_name,value in zip(stats_names,team_stats):
            if stat_name != " ":
                #stat_name = "Cup"
                team[stat_name] = value
    #print stat_name,value
    
    #expand_col = tree.xpath('//*[@id="tournamentstats"]/div[2]/div/div/div[@class="expandcol hidden"][1]')
    #print expand_col
    #another_div = tree.xpath('//*[@id="tournamentstats"]/div[2]/div/div/div[1]/div')
    #print another_div
    #hidden_table = tree.xpath('//*[@id="tournamentstats"]/div[2]/div/div/div[1]/div/table')
    #print hidden_table
    #problematic because the table is hidden until the chevron is clicked

def get_all_teams_data(base, teams_dict):
    "For the given teams, acquire general world cup data for each"
    for team in teams_dict:
        get_team_data(base,teams_dict[team])

def pretty_print_dict(my_dict):
    pp = pprint.PrettyPrinter(depth=3)
    pp.pprint(my_dict)

base = 'http://www.fifa.com'
teams_dict = get_teams(base)

#smaller set of teams to work with temporarily
country_names = { 'Chinese Taipei', 'Zambia', 'Canada', 'Germany','Brazil','Egypt' }
country_names = {'Brazil'}
test_dict = { key:value for key,value in teams_dict.items() if key in country_names }

get_all_teams_data(base, test_dict)
pretty_print_dict(test_dict)

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
