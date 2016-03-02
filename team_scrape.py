import requests
import pprint
from lxml import html
from itertools import islice

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def get_html_tree(url):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    return tree

def get_teams(base):
    "Get the names and links of the teams"
    #XPath of relevant stuff                                                                              
    # for the capitalized name, i think 
    # //*[@id="teamsBrowser"]/div[4]/div[1]/ul/li[1]/a/span                                               # for the team link                                                                                   # //*[@id="teamsBrowser"]/div[4]/div[1]/ul/li[1]/a
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

def get_team_data(base, teams_dict):
    "For a given team, acquire general world cup data"
    #general, over all world cups
    # //*[@id="tournamentstats"]/div[2]/div/div/ul[1]/li[2]/div[2]/span
    #specific world cup editions
    # //*[@id="tournamentstats"]/div[2]/div/div/div[1]/div/table/tbody/tr[1]/td[1]
    for team in teams_dict:
        link = teams_dict[team]["link"]
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
                    teams_dict[team][stat_name] = value
                #print stat_name,value

def pretty_print_dict(my_dict):
    pp = pprint.PrettyPrinter(depth=3)
    pp.pprint(my_dict)

base = 'http://www.fifa.com'
teams_dict = get_teams(base)

#smaller set of teams to work with temporarily
country_names = { 'Chinese Taipei', 'Zambia', 'Canada', 'Germany','Brazil','Egypt' }
test_dict = { key:value for key,value in teams_dict.items() if key in country_names }

get_team_data(base, test_dict)
pretty_print_dict(test_dict)
# TODO SPECIFIC WORLD CUP EDITIONS PER TEAM
