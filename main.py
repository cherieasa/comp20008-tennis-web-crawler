# Code by Terada Asavapakuna 1012869 - COMP20008 Elements of Data Processing Project 1
# import libraries
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import pandas as pd
import json

#----------------------------------- task 1 -----------------------------------

# webpage to crawl
base_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'

# the GET method indicates that you’re trying to get or retrieve data from a specified resource. 
page = requests.get(base_url)
soup = BeautifulSoup(page.text, 'html.parser')

# mark base page as visitied
visited = {}; 
visited[base_url] = True
pages_visited = 1

# list of visited + headings
list_URL = []
list_head = []

# find next links from base link
links = soup.findAll('a')
seed_link = soup.findAll('a', href=re.compile("^index.html"))
to_visit_relative = [l for l in links if l not in seed_link]

# Resolve to absolute urls
to_visit = []
for link in to_visit_relative:
    to_visit.append(urljoin(base_url, link['href']))
    
# visit pages in to_visit list (traversing like a tree)
while (to_visit) :

    # pop first link to visit
    link = to_visit.pop(0)

    # need to concat with base_url
    page = requests.get(link)

    # scraping code
    soup = BeautifulSoup(page.content, 'html.parser')
    heading = soup.findAll('h1')
    # add headings of articles to list_head
    for h1_tag in heading:
        list_head.append(h1_tag.text)

    # mark the item as visited, add to visited list, remove from to_visit
    visited[link] = True
    list_URL.append(link)
    
    # find connecting links on current link
    new_links = soup.findAll('a')
    for new_link in new_links :
        new_item = new_link['href']
        new_url = urljoin(link, new_item)
        # append new URL if haven't visited
        if new_url not in visited and new_url not in to_visit:
            to_visit.append(new_url)
    
    # keeps track of number of visited pages
    pages_visited = pages_visited + 1

print('\nvisited {0:5d} pages; {1:5d} pages in to_visit'.format(len(visited), len(to_visit)))

# create dataframe with URL and Heading as headings
d = {'url': list_URL, 'heading' : list_head}
df = pd.DataFrame(data=d)

# create csv file
df.to_csv('task1.csv', index = False)

#----------------------------------- task 2 -----------------------------------

# open tennis.json file

with open('tennis.json') as file:
  tennisdata = json.load(file)

count = 0
list_name = []
each_name = []
full_name = ''

# loop through JSON file for list of player names
for count in range(len(tennisdata)):
    each_name = tennisdata[count].get('name')
    list_name.append(each_name)

# visit every URL in list_URL
to_visit = list_URL.copy()

# list of list of words in each article
list_article = []

# list of words in a certain article
list_word = []
list_content = []

while(to_visit):

    # get first link in list and remove in to_visit
    link = to_visit.pop(0)

    # need to concat with base_url
    page = requests.get(link)

    # scarping code goes here
    soup = BeautifulSoup(page.content, 'html.parser')
    bodytext = soup.findAll('p')
    
    content = ""
    
    # separate each word in paragraph into list
    for paragraph in bodytext:
        list_word.extend((paragraph.text).split(" "))
        content += paragraph.text
        
    # remove text: prev, next article in list_word
    list_word = list_word[:-4]

    list_article.append(list_word)
    list_word = []
    list_content.append(content)

# cleanse punctuation in listarticle ONLY for names
# define punctuation and numbers but keeping hyphens
punctuations = '''!()[]{};:'",<>./?@#$%^&*~'''
numbers = '0123456789-'

no_punct_list1 = []
no_punct_list = []

# separate punctuation only to extract player names
for artwords in list_article:
    for word in artwords:
        no_punct = ""
        punct = ""
        for char in word:
            # if the character is a punc
            if (char in punctuations):
                punct = char
            
            # if the character is an alphabet or is in number (then form word)
            elif ((char not in punctuations) or (char in numbers)):
                no_punct = no_punct + char
             
        no_punct_list1.append(no_punct)
        
        # append punctuation only if it exists
        if (punct != ""):
            no_punct_list1.append(punct)
    
    # append list of words in article to list        
    no_punct_list.append(no_punct_list1)
    no_punct_list1 = []

# to find player names in articles    
name_list = []

for article in no_punct_list:
    counter = 0
    name_found = 0
    
    # look through each word
    for word in article:
        for name in list_name:
            if name in ' '.join(article[:counter+1]).upper():
                # if a name is found, add to our list and skip to next article
                name_list.append(name)
                name_found = 1
                break
        if name_found == 1:
            break
        else:
            counter += 1
    
    # if a name is not found, append "no name"
    if name_found == 0:
        name_list.append("no name")
        
# list of indexes of no names and no scores in articles
list_no_names_score_index = []
count_index = 0

# keeps indexes of no names in our name_list (to remove in name_list later)
for all_names in name_list:
    
    if all_names == 'no name':
        list_no_names_score_index.append(count_index)
    
    count_index += 1

# function to find first completed match score
def extract_first_complete_score(list_content):
    
    list_score = []
    score = ""
    
    # find valid score in article
    for content in list_content:
        score = re.search("(((6-[0-4]).)|((7-(6|5)).)|(([0-4]-6).)|(((6|5)-7).)|(\((\d{1,})(-|/)(\d{1,})\).)|((8|9|(\d\d))-([6-9]|(\d\d)))|(([6-9]|(\d\d))-(8|9|(\d\d)))){2,9}", content)
        
        # if there is a score present in an article, then append to list_score
        if (score):
            list_score.append(score[0])
        
        else:
            list_score.append("no score")
        
    return list_score

# list of scores in each article (but with punctuation)
score_list_punct = extract_first_complete_score(list_content)

# list of indexes of no scores in articles
count_index = 0

# keeps indexes of no scores in our score_list_punct (to remove in score_list_punct later)
for score in score_list_punct:
    
    if score == 'no score':
        if count_index not in list_no_names_score_index:
            list_no_names_score_index.append(count_index)
    
    count_index += 1
    
# function to cleanse articles with non-existing player names or scores
def cleanse_no_player_score(index_of_articles, list_we_want_to_cleanse):
    output_cleansed_list = []
    for i in range(len(list_we_want_to_cleanse)):
        if i not in index_of_articles:
            output_cleansed_list.append(list_we_want_to_cleanse[i])

    return output_cleansed_list

# cleanse extracted score_list - remove punctuations that are after or before score, excluding brackets
score_list = []
each_score_article = ""
for each_score in score_list_punct:
    for num_char in each_score:
        if num_char not in '''![]{};:'",<>.?@#$%^&*~''':
            each_score_article += num_char
    score_list.append(each_score_article)
    each_score_article = ""
     
# remove articles with no names and scores and output to task2.csv       
new_list_URL = cleanse_no_player_score(list_no_names_score_index, list_URL)
new_list_head = cleanse_no_player_score(list_no_names_score_index, list_head)
new_list_name = cleanse_no_player_score(list_no_names_score_index, name_list)
new_list_score = cleanse_no_player_score(list_no_names_score_index, score_list)


d = {'url': new_list_URL, 'heading' : new_list_head, 'player' : new_list_name, 'score' : new_list_score}
df = pd.DataFrame(data=d)

# create csv file
df.to_csv('task2.csv', index = False)
    
#----------------------------------- task 3 -----------------------------------

# remove tie break scores scores that start with "("
each_score1 = ""
no_tie_break = []

for each_score in new_list_score:
    for each_set in (each_score.strip()).split(" "):
        # if the set detected is a not a tiebreak
        #print(each_set)
        if each_set[0] != '(':
            # then add to our article score
            each_score1 += each_set + " "
            
    no_tie_break.append(each_score1)
    each_score1 = ""
    
# function to find game difference
def find_game_diff(no_tie_break_list):
    # initiate score
    game_diff = []
    player1 = 0
    player2 = 0
    for each_score in no_tie_break_list:
        for each_set in (each_score.strip()).split(" "):
            indexhypen = each_set.index("-")
            # player 1 scores come before "-" and player 2 after
            player1 += int(each_set[0:indexhypen])
            player2 += int(each_set[indexhypen+1:])
        
        game_diff.append(abs(player1-player2))
        player1 = 0
        player2 = 0
    
    return game_diff

# find game difference of list of scores with no tie break         
list_game_diff = find_game_diff(no_tie_break)      

found_names = []
found_scorediff = []
found_count = []
count = 1

# find the total game difference and count of each player (taking care of duplicates)
for i in range(len(new_list_name)):
    name = new_list_name[i]
    index = 0
    
    # if name is new in our list
    if name not in found_names:
        index = len(found_names)
        found_names.append(name)
        found_scorediff.append(0)
        found_count.append(0)
    
    # if name already exists, our index = the position of our pre-existing name
    else:
        index = found_names.index(name)
    
    # add score to that index    
    found_scorediff[index] += list_game_diff[i]
    # increase the count of that index
    found_count[index] += 1

# find average score difference for each player
list_avg = []

for i in range(len(found_scorediff)):
    list_avg.append(found_scorediff[i]/found_count[i])
    
d = {'player' : found_names, 'avg_game_difference' : list_avg}
df = pd.DataFrame(data=d)

# create csv file
df.to_csv('task3.csv', index = False)
    
#----------------------------------- task 4 -----------------------------------

# find the players with top 5 count number
lst = pd.Series(found_count)
max5index = lst.nlargest(5)
list_index = max5index.index.values.tolist()

# names of the top 5 most frequently written in article
list_name_max5 = []
# the number of times the top 5 most frequently written in article
list_count_max5 = []

for i in range(5):
    list_name_max5.append(found_names[list_index[i]])
    list_count_max5.append(found_count[list_index[i]])
    
d = {'player' : list_name_max5, 'number_of_times' : list_count_max5}
df = pd.DataFrame(data=d)   
     
# create graph using .plot
ax = df.plot( kind = 'bar', x = 'player', y = 'number_of_times', title = "Top 5 Most Written about Players vs their Count", rot = 90)
# label y axis
ax.set_ylabel('number_of_times')
graph = ax.get_figure()
# make graph picture fit task4.png using 'tight'
graph.savefig('task4.png', bbox_inches='tight')   
        
#----------------------------------- task 5 -----------------------------------

list_win_percent = []
# for our names in found_names, extract win percentage in the same order (index)
for i in range(len(found_names)):
    for count in range(len(tennisdata)):
        each_name = tennisdata[count].get('name')
        # if name exists in our list, extract win %
        if each_name == found_names[i]:
            percent = (tennisdata[count].get('wonPct'))
            # remove % symbol from percent data and convert to float type
            percent = percent[:-1]
            list_win_percent.append(float(percent))
            break

d = {'player': found_names, 'average_game_difference' : list_avg, 'win_percent': list_win_percent}
df = pd.DataFrame(data=d)

# width of bar
width = 0.2
# plot player vs average_game_difference in red
ax = df.plot(kind = 'bar', x = 'player', y = 'average_game_difference', color = 'red', width = width, position = 1, rot = 90)
ax.set_ylabel('average_game_difference')
# plot player vs win percent in blue on the same axes
ax2 = df.plot(kind = 'bar', x = 'player', y = 'win_percent', title = "Player vs Average Game Difference and Win Percent", secondary_y = True, color = 'blue', width = width, position = 0, ax=ax)
ax2.set_ylabel('win_percent (%)')

# move position of legend
ax.legend(bbox_to_anchor=(0.45, 0.97), ncol=1, mode="expand", borderaxespad=0., frameon=False)
ax2.legend(bbox_to_anchor=(0.45, 0.9), ncol=1, mode="expand", borderaxespad=0., frameon=False)
graph = ax.get_figure()

# make graph picture fit task5.png using 'tight'
graph.savefig('task5.png', bbox_inches='tight')           
