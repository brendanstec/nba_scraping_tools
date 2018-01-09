from __future__ import division
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import bs4 as bs
import urllib
import unicodedata
import datetime
import sys

########

def get_player_stats(player,year):

	'''
	Function that pulls in an NBA player's statistics as reported on basketball reference.
	Player is a string, year is a number referring to the year of the second half of the 
	season (e.g. enter 2015 for the 2014-2015 season). 
	
	get_player_stats('Lebron James', 2015)
	'''

	# depending on user's input, construct a dynamic url from basketball reference
	base_url = 'https://www.basketball-reference.com/players/'
	gamelog = 'gamelog/'
	player_id = get_id(player) #proprietary function to pull a player's unique id number
	letter = player_id.split()[0][0]
	#firstname = player.split()[0][:2]
	#number = '01'
	year = year
	final_url = base_url + letter + '/' + player_id + '/' + 'gamelog/' + str(year) + '/'

	sauce = urllib.urlopen(final_url).read() # open url
	soup = bs.BeautifulSoup(sauce,'lxml') # convert to soup oject
    
	stats = soup.find('table', {'id': 'pgl_basic'}) # find the stats table
	cols = [i.get_text() for i in stats.thead.find_all('th')] # find column headers
	cols = [x.encode('UTF8') for x in cols] # convert column headers to strings
	cols[5]='home_away' # rename
	cols[7]='win-loss' # rename
    
	data = [i.get_text().split('n') for i in stats.tbody.find_all('td')] # find all data points
	for i in range(len(data)):
		data[i] = [x.encode('UTF8') for x in data[i]] 
        
	data_list = [x[0] for x in data] #converts list of lists to straight list (easier to work with)
    
	zeros = [0]*22 # create a list of zeros; we will fill in missing games with this to keep list formatted correctly
    
	strings = ['Did Not Play','I','Did Not Dress','Not With Team','Player Suspended','Player Suspe'] # 'I' stands for Inactive
	grow_amount = sum(data_list.count(x) for x in strings) * 21 
    # grow_amount meaning: as we are replacing 'Did Not Plays' or 'I's' with zeros, the total list grows
    # We need the loop to stop at the end of the growing list, not the end of the original one
  
  	# This section just replaces the 'Did Not Plays' and 'I's' with zeros of appropriate length
	for i in range(len(data_list)+grow_amount-1):
		#if data_list[i] == 'Did Not Play' or data_list[i] == 'I' or data_list[i] == 'Did Not Dress': 
		if data_list[i] in strings:             
			data_list[i:i+1]=zeros #
        
	new_cols = cols[1:]
	num_rows = len(data_list) / 29 # usually 82; depends on year though (the formatting changes)
    
	df = pd.DataFrame(np.array(data_list).reshape(num_rows,29), columns = new_cols) # reshape list into dataframe 
    
	#df = df.convert_objects(convert_numeric=True) # convert into numbers (CURRENTLY DEPRECATED) OLD METHOD
	
	df[['GS','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL',
    'BLK','TOV','PF','PTS','GmSc','+/-']] = df[['GS','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL',
    'BLK','TOV','PF','PTS','GmSc','+/-']].apply(pd.to_numeric)
    
	#df = df[df.G != ''] #added on November 11, 2017. We don't want dataframe longer than 82 rows. Eliminate games
	#where the player didn't play at all because was recently added to team. Ersan Ilyasova is an example.
    
	#df.set_index([range(82)],inplace=True) #also added on November 11, 2017 to eliminate key errors. 
    
	return df

########