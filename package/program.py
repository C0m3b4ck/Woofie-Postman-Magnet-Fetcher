# ///////////// LIBRARY IMPORTS ////////////////////
import os
import time
import pyfiglet
import random
from bs4 import BeautifulSoup
import urllib
import urllib.request
import requests
# ///////////// GLOBAL VARIABLES ///////////////////
postman_url = ""
category_list = ["movies", "music", "tv", "games", "apps", "misc", "pictures", "anime", "comics", "social media", "podcasts", "books", "audiobooks", "ebooks", "course/lesson", "essay/op-ed", "cad/3d-printing", "music vid", "pr0n", "documentary", "leaked documents", "conspiracy", "religious content"]
selected_category = 0
show_per_page = 0
view = ""
orderby_map = [-1, 1, 2, 3, 4, 5, 6, 7]
orderby_list = ["descending", "time added", "downloads", "hits", "comments", "swarmsize", "rating", "torrentsize"]
orderby_num = -1
lastactive_map = [-1, 1, 2, 3, 4, 5, 6, 7, 8]
lastactive_list = ["active torrents", "active last 24h", "active last 48h", "active last week", "active last 2weeks", "w/o seeders", "abandoned torrents", "cross seed torrents", "all torrents"]
lastactive_num = -1
language_map = [-1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
language_list = ["any language", "english", "german", "french", "spanish", "potuguese", "dutch", "russian", "swedish", "italian", "chinese", "finnish", "japanese", "turkish", "korean", "danish", "norwegian", "polish", "hindi"]
language_num = -1
seed = None
from_waittime = 0
to_waittime = 0
torrent_numer = 0 # postman does not have a page system, they instead use start_torrent_num to end_torrent_num for showing torrents
# ///////////// USER INTERACTION ///////////////////
def greet():
	string_to_print = pyfiglet.figlet_format("Postman Magnet Fetcher", font="slant")
	print(string_to_print)
	dog_ascii = r"""
	     .--~~,__
:-....,-------`~~'._.'
 `-,,,  ,_      ;'~U'
  _,-' ,'`-__; '--.
 (_/'~~      ''''(;
"""
	print(dog_ascii)
	string_to_print = pyfiglet.figlet_format("By C0m3b4ck")
	print(string_to_print)
	time.sleep(2)
	print("!!! Postman forbids using scripts on the site, therefore be EXTRA RESPECTFUL !!!")
	time.sleep(2)
def goodbye():
	string_to_print = pyfiglet.figlet_format("Goodbye", font="slant")
	print(string_to_print)
	dog_ascii = r"""
             .--~~,__
:-....,-------`~~'._.'
 `-,,,  ,_      ;'~U'
  _,-' ,'`-__; '--.
 (_/'~~      ''''(;
"""

	print(dog_ascii)

def get_postman_url():
	global postman_url
	print("/// Default URL is tracker2.postman.i2p ///")
	postman_url = input("Input Postman Tracker URL (empty for default): ")
	if postman_url == "":
		postman_url = "http://tracker2.postman.i2p"
def get_category():
	global selected_category
	selected_category = ""
	while not selected_category.lower() in category_list:
		selected_category = input("Input category: ")
		if not selected_category.lower() in category_list:
			print("!!! Invalid category: ", selected_category)
			print("Please input valid category.")
	# map category to number for Postman compatibility
	selected_category = category_list.index(selected_category.lower()) + 1
def get_show_per_page():
	global show_per_page
	show_per_page = ""
	while show_per_page == "":
		show_per_page = int(input("Input show per page number: "))
		# //// add checking if show per page is above maximum
		if show_per_page <= 0:
			print("!!! Show per page cannot be 0 or less !!!")
			show_per_page = ""
def get_view():
	global view
	view = ""
	view = input("Input view (leave empty for main): ")
	if view == "":
		view = "Main"
def get_lang():
	global language_num
	# -1 is any language
	language_str = ""
	while not language_str.lower() in language_list:
		language_str = input("Input language: ")
		if not language_str.lower() in language_list:
			print("!!! Unrecognized language !!!")
	language_num = language_map[language_list.index(language_str.lower())] # gets number by getting string position in string array, then getting that element number from number array
def get_orderby():
	global orderby_num
	# -1 is descending, 0 skipped, time added is 1
	orderby_str = ""
	while not orderby_str.lower() in orderby_list:
		orderby_str = input("Input order by: ")
		if not orderby_str.lower() in orderby_list:
			print("!!! Unrecognized order by option !!!")
	orderby_num = orderby_map[orderby_list.index(orderby_str.lower())] # gets number by getting string position in string array, then getting that element number from number array
def get_lastactive():
	global lastactive_num
	lastactive_str = ""
	while not lastactive_str.lower() in lastactive_list:
		lastactive_str = input("Input last active: ")
		if not lastactive_str.lower() in lastactive_list:
			print("!!! Unrecognized last active option !!!")
	lastactive_num = lastactive_map[lastactive_list.index(lastactive_str.lower())] # gets number by getting string position in string array, then getting that element number from number array
def get_waittimes(): # <--- potentially remove
	global seed, from_waittime, to_waittime
	seed = None
	while seed == None:
		seed = int(input("Input randomization seed: "))
		if seed == None:
			print("!!! Error: seed cannot be null !!!")
	random.seed(seed)
	while from_waittime == 0:
		from_waittime = int(input("Input minimum waittime in seconds (at least 10s): "))
		if from_waittime < 10:
			print("!!! Waittime must be more than 10 seconds !!!")
			from_waittime = 0
	while to_waittime == 0:
		to_waittime = int(input("Input minimum waittime in seconds (at least 10s): "))
		if to_waittime < 10:
			print("!!! Waittime must be more than 10 seconds !!!")
			to_waittime = 0
def out_allvars():
	print("Postman URL: ", postman_url)
	print("Selected category: ", selected_category)
	print("Show per page: ", show_per_page)
	print("View: ", view)
	print("Language: ", language_list[language_map.index(language_num)])
	print("Order by: ", orderby_list[orderby_map.index(orderby_num)])
	print("Last active: ", lastactive_list[lastactive_map.index(lastactive_num)])
	print("Wait time from: ", from_waittime, ", To: ", to_waittime)
def get_user_input():
	get_postman_url()
	get_category()
	get_show_per_page()
	get_view()
	get_lang()
	get_orderby()
	get_lastactive()
	get_waittimes() # <--- potentially remove
	out_allvars()
# //////////// NETWORKING ///////////////
def download_wget(url): # <--- potentially remove
	print("wget url: ", url)
	subprocess.run("http_proxy=127.0.0.1:4444 wget " + url)
def download_page(url, file_name):
	i2p_proxy = urllib.request.ProxyHandler({'http': '127.0.0.1:4444'})
	opener = urllib.request.build_opener(i2p_proxy)
	urllib.request.install_opener(opener)
	f = urllib.request.urlretrieve(url, file_name)
def authenticate_form_token(file_name):
    http_proxy  = "http://127.0.0.1:4444"
    proxies = {
                  "http"  : http_proxy,
                }
    lander = requests.get(postman_url, proxies=proxies)
    lander_file = open("lander.html", 'w')
    lander_file.write(str(lander))
    lander_file.close()
    with open(r'lander.html', 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            searchstring = ('name="formtoken" value="') # String to search for
            if row.find(searchstring) != -1:
                print('Found form token! :)')
                print('Line Number:', lines.index(row))
                content = fp.readlines()
                token = content[lines.index(row)].split('value="')[1].split('"')[0]


# --------------> getting torrent links (not magnet links)
# craft URL: postman_url + all the options + page num
# get one page of results
# convert html to text
# sanitize html, only leave torrent links
# input torrent links from file into table
# ask user about each one (maybe implement something SQL-esq later on, for example - exclude certain keywords)
# save user preferences for all (two seperate files - one with yes, one with no)
### <-> repeat for all result pages
# get magnet links of the torrents that the user wanted (implement wait time here)
# SOMEHOW add them into i2psnark (i2psnark standalone?)
# /////////// MAIN FUNCTION /////////////
if __name__ == "__main__":
	greet()

	get_user_input()
	# some networking calls here
	download_page(postman_url, "example.html")

	goodbye()
	exit()
