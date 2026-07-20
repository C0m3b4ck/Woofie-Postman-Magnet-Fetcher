# ///////////// LIBRARY IMPORTS ////////////////////
import os
import re
import sys
import json
import time
import atexit
import pyfiglet
import urllib.parse
import urllib.request
import urllib.error
import requests

# ///////////// ANSI COLORS ///////////////////
RED = '\033[91m'
GREEN = '\033[32m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
DARK_PURPLE = '\033[35m'
BRIGHT_GREEN = '\033[92m'
RESET = '\033[0m'

def print_error(msg):
	print(f"{RED}[ERROR] {msg}{RESET}")

def print_success(msg):
	print(f"{GREEN}[OK] {msg}{RESET}")

def print_warning(msg):
	print(f"{YELLOW}[!] {msg}{RESET}")

def print_info(msg):
	print(f"{BLUE}{msg}{RESET}")

def input_blue(prompt):
	return input(f"{BLUE}{prompt}{RESET}")

def ascii_brightgreen(msg):
	print(f"{BRIGHT_GREEN}{msg}{RESET}")

def ascii_darkpurple(msg):
	print(f"{DARK_PURPLE}{msg}{RESET}")
# ///////////// GLOBAL VARIABLES ///////////////////
dog_ascii = r"""
            .--~~,__
:-....,-------`~~'._.'
`-,,,  ,_      ;'~U'
 _,-' ,'`-__; '--.
(_/'~~      ''''(;
"""
postman_url = ""
category_list = ["movies", "music", "tv", "games", "apps", "misc", "pictures", "anime", "comics", "social media", "podcasts", "books", "audiobooks", "ebooks", "course/lesson", "essay/op-ed", "cad/3d-printing", "music vid", "pr0n", "documentary", "leaked documents", "conspiracy", "religious content"]
selected_category = 0
show_per_page = 0
limit = 0
view = "Main"
orderby_map = [-1, 1, 2, 3, 4, 5, 6, 7]
orderby_list = ["descending", "time added", "downloads", "hits", "comments", "swarmsize", "rating", "torrentsize"]
orderby_num = None
lastactive_map = [-1, 1, 2, 3, 4, 5, 6, 7, 8]
lastactive_list = ["active torrents", "active last 24h", "active last 48h", "active last week", "active last 2weeks", "w/o seeders", "abandoned torrents", "cross seed torrents", "all torrents"]
lastactive_num = None
language_map = [-1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
language_list = ["any language", "english", "german", "french", "spanish", "potuguese", "dutch", "russian", "swedish", "italian", "chinese", "finnish", "japanese", "turkish", "korean", "danish", "norwegian", "polish", "hindi"]
language_num = None
seed = None
from_waittime = 0
to_waittime = 0
torrent_number = 0 # postman does not have a page system, they instead use start_torrent_num to end_torrent_num for showing torrents
start_page = 1
to_add = [] # stores magnet links the user wants to add
not_add = [] # stores magnet links the user does not want
not_wanted_magnets = [] # loaded from not_wanted_magnets.txt for filtering
filter_not_wanted = False
filter_danger = False
danger_words = []
filter_copyright = False
copyright_words = []
filter_disk_limit = False
disk_limit_gb = 0
current_selection_sizes = []
hands_on_mode = False
add_all_mode = False
min_waittime = 10
max_waittime = 30
token = ""
search = ""
http_proxy = "127.0.0.1:4444"
DEFAULT_PROXY = "127.0.0.1:4444"
NOT_WANTED_FILE = "not_wanted_magnets.txt"
CONFIG_FILE = "config.json"
DANGER_WORDS_FILE = "danger_words.txt"
COPYRIGHT_WORDS_FILE = "copyright_words.txt"
TEMP_FILES = ["lander.html", "post_response.html", "fetched_page.html"]
I2PSNARK_URL = "http://127.0.0.1:7657/i2psnark/"
DEFAULT_DANGER_WORDS = ["guns", "explosives", "drugs", "narcotics", "weapons", "bomb", "poison", "firearm", "ammunition", "knives"]
DEFAULT_COPYRIGHT_WORDS = ["marvel", "disney", "netflix", "hbo", "paramount", "warner", "universal", "sony", "pixar", "lucasfilm", "20th century fox", "columbia", "mgm", "amazon", "apple", "hulu", "crunchyroll", "funimation", "blizzard", "riot games", "ea games", "ubisoft", "rockstar", "activision", "konami", "capcom", "square enix", "bandai", "nintendo", "sega", "microsoft", "adobe", "microsoft office"]

def cleanup():
	for f in TEMP_FILES:
		if os.path.exists(f):
			os.remove(f)

atexit.register(cleanup)
# ///////////// CONFIG ///////////////////
def load_config():
	if not os.path.exists(CONFIG_FILE):
		return {}
	with open(CONFIG_FILE, 'r') as f:
		return json.load(f)

def save_config(settings):
	with open(CONFIG_FILE, 'w') as f:
		json.dump(settings, f, indent=4)

def apply_config(settings):
	global postman_url, http_proxy, I2PSNARK_URL, filter_danger, danger_words, filter_copyright, copyright_words, filter_disk_limit, disk_limit_gb, hands_on_mode, add_all_mode, min_waittime, max_waittime
	if "tracker_url" in settings:
		postman_url = settings["tracker_url"]
	if "http_proxy" in settings:
		http_proxy = settings["http_proxy"]
	if "i2psnark_url" in settings:
		I2PSNARK_URL = settings["i2psnark_url"]
	if "filter_danger" in settings:
		filter_danger = settings["filter_danger"]
	if "danger_words" in settings:
		danger_words = settings["danger_words"]
	if "filter_copyright" in settings:
		filter_copyright = settings["filter_copyright"]
	if "copyright_words" in settings:
		copyright_words = settings["copyright_words"]
	if "filter_disk_limit" in settings:
		filter_disk_limit = settings["filter_disk_limit"]
	if "disk_limit_gb" in settings:
		disk_limit_gb = settings["disk_limit_gb"]
	if "hands_on_mode" in settings:
		hands_on_mode = settings["hands_on_mode"]
	if "add_all_mode" in settings:
		add_all_mode = settings["add_all_mode"]
	if "min_waittime" in settings:
		min_waittime = settings["min_waittime"]
	if "max_waittime" in settings:
		max_waittime = settings["max_waittime"]

def get_router_type():
	global I2PSNARK_URL
	settings = load_config()
	if settings:
		choice = input_blue("Load saved settings from config.json? y/n: ").strip().lower()
		if choice in ('y', 'yes'):
			apply_config(settings)
			print_success("Loaded settings from config.json")
			modify = input_blue("Modify settings? y/n: ").strip().lower()
			if modify not in ('y', 'yes'):
				return True
		else:
			print_info("Proceeding with default settings.")
	print_info("Select your i2p router type:")
	print_info("  1) Official I2P router (default port 7657)")
	print_info("  2) I2P standalone (default port 8002)")
	while True:
		choice = input_blue("Choice (1/2): ").strip()
		if choice == "1":
			I2PSNARK_URL = "http://127.0.0.1:7657/i2psnark/"
			break
		elif choice == "2":
			I2PSNARK_URL = "http://127.0.0.1:8002/i2psnark/"
			break
		else:
			print_error("Invalid choice. Enter 1 or 2.")
	return False

def prompt_save_settings():
	print_info("Save current settings for next run? y/n")
	choice = input_blue("Save settings? y/n: ").strip().lower()
	if choice in ('y', 'yes'):
		settings = {
			"tracker_url": postman_url,
			"http_proxy": http_proxy,
			"i2psnark_url": I2PSNARK_URL,
			"filter_danger": filter_danger,
			"danger_words": danger_words,
			"filter_copyright": filter_copyright,
			"copyright_words": copyright_words,
			"filter_disk_limit": filter_disk_limit,
			"disk_limit_gb": disk_limit_gb,
			"hands_on_mode": hands_on_mode,
			"add_all_mode": add_all_mode,
			"min_waittime": min_waittime,
			"max_waittime": max_waittime
		}
		save_config(settings)
		print_success("Settings saved to config.json")
# ///////////// DANGER FILTER ///////////////////
def load_danger_words():
	global danger_words
	if danger_words:
		return
	if os.path.exists(DANGER_WORDS_FILE):
		with open(DANGER_WORDS_FILE, 'r') as f:
			danger_words = [line.strip().lower() for line in f if line.strip()]
	else:
		danger_words = DEFAULT_DANGER_WORDS[:]

def save_danger_words():
	with open(DANGER_WORDS_FILE, 'w') as f:
		for word in danger_words:
			f.write(word + '\n')

def get_danger_filter():
	global filter_danger
	load_danger_words()
	print_info("Enable danger filter? y/n")
	print_info(f"Filters: {', '.join(danger_words)}")
	choice = input_blue("Danger filter? y/n: ").strip().lower()
	if choice in ('y', 'yes'):
		filter_danger = True
		print_success("Danger filter enabled.")
	else:
		filter_danger = False
		print_info("Danger filter disabled.")

def check_danger(title):
	title_lower = title.lower()
	for word in danger_words:
		if word.lower() in title_lower:
			return True
	return False
# ///////////// COPYRIGHT FILTER ///////////////////
def load_copyright_words():
	global copyright_words
	if copyright_words:
		return
	if os.path.exists(COPYRIGHT_WORDS_FILE):
		with open(COPYRIGHT_WORDS_FILE, 'r') as f:
			copyright_words = [line.strip().lower() for line in f if line.strip()]
	else:
		copyright_words = DEFAULT_COPYRIGHT_WORDS[:]

def save_copyright_words():
	with open(COPYRIGHT_WORDS_FILE, 'w') as f:
		for word in copyright_words:
			f.write(word + '\n')

def get_copyright_filter():
	global filter_copyright
	load_copyright_words()
	print_info("Enable copyright filter? y/n")
	print_info(f"Filters: {', '.join(copyright_words[:10])}...")
	choice = input_blue("Copyright filter? y/n: ").strip().lower()
	if choice in ('y', 'yes'):
		filter_copyright = True
		print_success("Copyright filter enabled.")
	else:
		filter_copyright = False
		print_info("Copyright filter disabled.")

def check_copyright(title):
	title_lower = title.lower()
	for word in copyright_words:
		if word.lower() in title_lower:
			return True
	return False
# ///////////// DISK SPACE LIMIT ///////////////////
def parse_size_to_gb(size_str):
	size_str = size_str.strip().upper()
	multipliers = {
		'B': 1 / (1024**3),
		'KB': 1 / (1024**2),
		'MB': 1 / 1024,
		'GB': 1,
		'TB': 1024,
	}
	for suffix, mult in multipliers.items():
		if size_str.endswith(suffix):
			try:
				num = float(size_str[:-len(suffix)].strip())
				return num * mult
			except ValueError:
				return None
	return None

def parse_peers(row):
	try:
		seed_idx = row.find('seed')
		if seed_idx == -1:
			return None, None
		before_seed = row[:seed_idx]
		nums = []
		for part in before_seed.split('>'):
			part = part.strip().replace(',', '')
			if part.isdigit():
				nums.append(int(part))
		if len(nums) >= 2:
			return nums[-2], nums[-1]
		return None, None
	except (ValueError, IndexError):
		return None, None

def parse_size_from_row(row):
	try:
		for suffix in ['TB', 'GB', 'MB', 'KB', 'B']:
			idx = row.find(suffix)
			if idx == -1:
				continue
			start = idx
			while start > 0 and (row[start-1].isdigit() or row[start-1] == '.' or row[start-1] == ' '):
				start -= 1
			size_str = row[start:idx+len(suffix)]
			result = parse_size_to_gb(size_str)
			if result is not None:
				return result
	except (ValueError, IndexError):
		return None
	return None

def get_disk_limit():
	global filter_disk_limit, disk_limit_gb
	print_info("Set disk space limit for torrents? y/n")
	choice = input_blue("Enable disk limit? y/n: ").strip().lower()
	if choice in ('y', 'yes'):
		filter_disk_limit = True
		while True:
			try:
				input_str = input_blue("Max total size in GB (e.g. 10.5): ").strip()
				disk_limit_gb = float(input_str)
				if disk_limit_gb <= 0:
					print_error("Size must be positive !!!")
					continue
				print_success(f"Disk limit set to {disk_limit_gb} GB")
				break
			except ValueError:
				print_error("Please enter a valid number !!!")
	else:
		filter_disk_limit = False
		print_info("Disk limit disabled.")

def get_hands_on_mode():
	global hands_on_mode
	print_info("Enable hands-on mode? (allows adding danger-flagged torrents)")
	choice = input_blue("Hands-on mode? y/n: ").strip().lower()
	if choice in ('y', 'yes'):
		hands_on_mode = True
		print_success("Hands-on mode enabled. Danger-flagged torrents will show red warning but can be added.")
	else:
		hands_on_mode = False
		print_info("Hands-on mode disabled.")

def get_add_all_mode():
	global add_all_mode
	print_info("Enable add-all mode? (auto-add all magnets without asking)")
	choice = input_blue("Add-all mode? y/n: ").strip().lower()
	if choice in ('y', 'yes'):
		add_all_mode = True
		print_success("Add-all mode enabled.")
	else:
		add_all_mode = False
		print_info("Add-all mode disabled.")

def get_waittime():
	global min_waittime, max_waittime
	print_info("Set wait time between pages (min 10 seconds)")
	while True:
		try:
			min_str = input_blue("Min wait time in seconds (default 10): ").strip() or "10"
			min_waittime = int(min_str)
			if min_waittime < 10:
				print_error("Minimum wait time must be at least 10 seconds !!!")
				continue
			max_str = input_blue("Max wait time in seconds (default 30): ").strip() or "30"
			max_waittime = int(max_str)
			if max_waittime < min_waittime:
				print_error("Max must be greater than or equal to min !!!")
				continue
			print_success(f"Wait time set to {min_waittime}-{max_waittime} seconds")
			break
		except ValueError:
			print_error("Please enter valid numbers !!!")

def check_disk_limit(size_gb):
	global disk_limit_gb
	total_size = sum(parse_size_to_gb(s) for s in current_selection_sizes if parse_size_to_gb(s) is not None)
	if total_size + size_gb > disk_limit_gb:
		return False
	return True
# ///////////// USER INTERACTION ///////////////////
def greet():
    global dog_ascii
    string_to_print = pyfiglet.figlet_format("Woofie I2P Postman Magnet Fetcher", font="slant")
    ascii_brightgreen(string_to_print)
    ascii_brightgreen(dog_ascii)
    string_to_print = pyfiglet.figlet_format("By C0m3b4ck")
    ascii_darkpurple(string_to_print)
    time.sleep(2)
    print_warning("Postman forbids using scripts on the site, therefore be EXTRA RESPECTFUL !!!")
    time.sleep(2)
def goodbye():
    global dog_ascii
    string_to_print = pyfiglet.figlet_format("Goodbye", font="slant")
    ascii_brightgreen(string_to_print)
    ascii_brightgreen(dog_ascii)

def get_postman_url():
	global postman_url
	print_info(f"/// Current tracker URL: {postman_url or 'tracker2.postman.i2p/'} ///")
	postman_url = input_blue("Input Postman Tracker URL (empty to keep current): ")
	if postman_url == "":
		if not globals().get('postman_url'):
			postman_url = "http://tracker2.postman.i2p/"
		return
	if not postman_url.startswith(("http://", "https://")):
		print_error("URL must start with http:// or https:// !!!")
		postman_url = "http://tracker2.postman.i2p/"
def get_category():
	global selected_category
	print_info("Available categories:")
	for i, cat in enumerate(category_list):
		print_info(f"  {i+1}. {cat}")
	while True:
		user_input = input_blue("Input category (name or number): ").strip()
		if user_input.isdigit():
			num = int(user_input)
			if 1 <= num <= len(category_list):
				selected_category = num
				return
			print_error(f"Number must be between 1 and {len(category_list)} !!!")
		elif user_input.lower() in category_list:
			selected_category = category_list.index(user_input.lower()) + 1
			return
		else:
			print_error("Invalid category: " + user_input)
def get_show_per_page():
	global show_per_page
	show_per_page = ""
	while show_per_page == "":
		try:
			show_per_page = int(input_blue("Input show per page number: "))
			# //// add checking if show per page is above maximum
			if show_per_page <= 0:
				print_error("Show per page cannot be 0 or less !!!")
				show_per_page = 0
		except ValueError:
			print_error("Please enter a valid number !!!")
def get_view():
	global view
	view_input = input_blue("Input view (leave empty for main): ")
	if view_input != "":
		view = view_input
def get_lang():
	global language_num
	print_info("Available languages:")
	for i, lang in enumerate(language_list):
		print_info(f"  {i}. {lang}")
	while True:
		user_input = input_blue("Input language (name or number): ").strip()
		if user_input.isdigit():
			num = int(user_input)
			if 0 <= num < len(language_list):
				language_num = language_map[num]
				return
			print_error(f"Number must be between 0 and {len(language_list) - 1} !!!")
		elif user_input.lower() in language_list:
			language_num = language_map[language_list.index(user_input.lower())]
			return
		else:
			print_error("Unrecognized language: " + user_input)
def get_orderby():
	global orderby_num
	print_info("Available order by options:")
	for i, opt in enumerate(orderby_list):
		print_info(f"  {i}. {opt}")
	while True:
		user_input = input_blue("Input order by (name or number): ").strip()
		if user_input.isdigit():
			num = int(user_input)
			if 0 <= num < len(orderby_list):
				orderby_num = orderby_map[num]
				return
			print_error(f"Number must be between 0 and {len(orderby_list) - 1} !!!")
		elif user_input.lower() in orderby_list:
			orderby_num = orderby_map[orderby_list.index(user_input.lower())]
			return
		else:
			print_error("Unrecognized order by option: " + user_input)
def get_lastactive():
	global lastactive_num
	print_info("Available last active options:")
	for i, opt in enumerate(lastactive_list):
		print_info(f"  {i}. {opt}")
	while True:
		user_input = input_blue("Input last active (name or number): ").strip()
		if user_input.isdigit():
			num = int(user_input)
			if 0 <= num < len(lastactive_list):
				lastactive_num = lastactive_map[num]
				return
			print_error(f"Number must be between 0 and {len(lastactive_list) - 1} !!!")
		elif user_input.lower() in lastactive_list:
			lastactive_num = lastactive_map[lastactive_list.index(user_input.lower())]
			return
		else:
			print_error("Unrecognized last active option: " + user_input)
def get_httpproxy():
	global http_proxy
	http_proxy_input = input_blue("Input HTTP proxy (empty for 127.0.0.1:4444): ")
	if not http_proxy_input == "":
		if re.match(r'^[\w.-]+:\d+$', http_proxy_input):
			http_proxy = http_proxy_input
		else:
			print_error("Invalid proxy format (expected host:port) !!!")
def get_limit_per_page():
	global limit
	while limit == 0:
		try:
			limit = int(input_blue("Input torrent per page limit: "))
			# //// add checking if limit is above maximum
			if limit <= 0:
				print_error("Limit cannot be 0 or less !!!")
				limit = 0
		except ValueError:
			print_error("Please enter a valid number !!!")
def get_search_term():
	global search
	search_input = input_blue("Input search term (can be empty): ")
	if search_input == "":
		search = ""
	else:
		search = search_input
def get_start_page():
	global start_page, torrent_number
	start_page = int(input_blue("Start from page number (default 1): ") or "1")
	if start_page < 1:
		print_error("Page number must be at least 1.")
		start_page = 1
	torrent_number = (start_page - 1) * limit
def load_not_wanted():
	global not_wanted_magnets, filter_not_wanted
	if not os.path.exists(NOT_WANTED_FILE):
		return
	with open(NOT_WANTED_FILE, 'r') as f:
		not_wanted_magnets = [line.strip() for line in f if line.strip()]
	if not not_wanted_magnets:
		return
	print_info(f"Found {len(not_wanted_magnets)} previously rejected magnet(s) in {NOT_WANTED_FILE}")
	choice = input_blue("Filter out rejected magnets? y/n: ")
	while choice.lower() not in ('y', 'n'):
		choice = input_blue("Filter out rejected magnets? y/n: ")
	if choice.lower() == 'y':
		filter_not_wanted = True
		print_success("Will skip previously rejected magnets.")
	else:
		print_info("Will show all magnets including previously rejected ones.")
def out_allvars():
	print_info("=== Current Settings ===")
	print_info(f"  Tracker URL: {postman_url}")
	print_info(f"  HTTP proxy: {http_proxy}")
	print_info(f"  i2psnark URL: {I2PSNARK_URL}")
	print_info(f"  Category: {category_list[selected_category - 1]}")
	print_info(f"  Show per page: {show_per_page}")
	print_info(f"  Limit per page: {limit}")
	print_info(f"  Starting page: {start_page}")
	print_info(f"  View: {view}")
	print_info(f"  Language: {language_list[language_map.index(language_num)]}")
	print_info(f"  Order by: {orderby_list[orderby_map.index(orderby_num)]}")
	print_info(f"  Last active: {lastactive_list[lastactive_map.index(lastactive_num)]}")
	print_info(f"  Search term: {search or '(none)'}")
	print_info(f"  Danger filter: {'ON' if filter_danger else 'OFF'}")
	print_info(f"  Copyright filter: {'ON' if filter_copyright else 'OFF'}")
	print_info(f"  Disk limit: {f'{disk_limit_gb} GB' if filter_disk_limit else 'OFF'}")
	print_info(f"  Hands-on mode: {'ON (can override danger filter)' if hands_on_mode else 'OFF'}")
	print_info(f"  Add all mode: {'ON (auto-add all magnets)' if add_all_mode else 'OFF'}")
	print_info(f"  Wait time: {min_waittime}-{max_waittime}s between pages")
	print_info("========================")
def get_user_input():
	settings_loaded = get_router_type()
	if not settings_loaded:
		get_postman_url()
		get_category()
		get_show_per_page()
		get_limit_per_page()
		get_search_term()
		get_start_page()
		get_view()
		get_lang()
		get_orderby()
		get_lastactive()
		get_httpproxy()
		get_danger_filter()
		get_copyright_filter()
		get_disk_limit()
		get_hands_on_mode()
		get_add_all_mode()
		get_waittime()
	load_not_wanted()
	out_allvars()
	prompt_save_settings()
# //////////// NETWORKING ///////////////
def download_page(url, file_name):
	proxy_url = http_proxy
	if not proxy_url.startswith("http://"):
		proxy_url = "http://" + proxy_url
	i2p_proxy = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
	opener = urllib.request.build_opener(i2p_proxy)
	try:
		response = opener.open(url, timeout=60)
		with open(file_name, 'wb') as f:
			f.write(response.read())
		return True
	except urllib.error.HTTPError as e:
		if e.code == 503:
			print_error("Server returned 503 - you are being throttled or the tracker is overloaded.")
			print_error("Try again in a few minutes, or increase your wait time between requests.")
		elif e.code == 403:
			print_error("Access forbidden (403). The tracker may be blocking your request.")
		elif e.code == 404:
			print_error("Page not found (404). Check the tracker URL.")
		else:
			print_error(f"HTTP error {e.code}: {e.reason}")
		return False
	except urllib.error.URLError as e:
		print_error(f"Could not connect to tracker: {e.reason}")
		print_error("Make sure your proxy is running and the URL is correct.")
		return False
	except IOError as e:
		print_error(f"Network error: {e}")
		return False
def authenticate_form_token():
	global token
	global http_proxy
	# proxy set for requests
	proxies = {
		"http"  : http_proxy,
	}
	session = requests.Session()
	session.proxies = proxies
	print_info("---> Getting form token... ")
	if not download_page(postman_url, "lander.html"):
		return
	print_success("Downloaded landing page")
	print_info("Opening lander.html in order to find token.")
	try:
		with open(r'lander.html', 'r') as fp:
			for line_num, row in enumerate(fp):
				searchstring = ('name="formtoken" value="')  # String to search for
				if row.find(searchstring) != -1:
					print_success('Found form token! :)')
					print_info('Line Number: ' + str(line_num))
					token = row.split('value="')[1].split('"')[0]
					print_success("FORMTOKEN: " + token)

					# send POST request here ?/action=Enter
					url_tok = postman_url + 'index.php?action=Enter'
					data_tok = {'formtoken' : token}

					x = session.post(url_tok, data = data_tok, timeout=60)

					if x.status_code == 200:
						print_success("Token submitted successfully (200)")
					else:
						http_errors = {
							400: "Bad Request - the tracker rejected your submission",
							403: "Forbidden - you may be blocked or not authorized",
							404: "Not Found - check the tracker URL",
							429: "Too Many Requests - you are being rate limited, wait before retrying",
							500: "Internal Server Error - the tracker is having issues",
							502: "Bad Gateway - proxy or tracker gateway error",
							503: "Service Unavailable - tracker is overloaded or down for maintenance",
							504: "Gateway Timeout - proxy or tracker took too long to respond",
						}
						msg = http_errors.get(x.status_code, f"HTTP {x.status_code}")
						print_error(f"Token submission failed: {msg}")
						print_warning("The script may not work correctly. Consider waiting and retrying.")
						with open('post_response.html', 'w') as f:
							f.write(x.text)
						return
					with open('post_response.html', 'w') as f:
						f.write(x.text)
					break
	except requests.RequestException as e:
		print_error(f"Network error during token submission: {e}")
	except IOError as e:
		print_error(f"Could not read lander.html: {e}")
def magnets_from_page():
	global postman_url, torrent_number, to_add, not_add, current_selection_sizes
	magnets = []
	titles = []
	sizes = []
	danger_flags = []
	params = urllib.parse.urlencode({
		'view': f"{view}Tab",
		'start': torrent_number,
		'limit': limit,
		'search': search,
		'category': selected_category,
		'orderby': orderby_num,
		'lastactive': lastactive_num,
		'lang': language_num
	})
	page_url = f"{postman_url}/index.php?{params}"
	print_info("---> Getting page: " + page_url)
	if not download_page(page_url, "fetched_page.html"):
		return
	with open(r'fetched_page.html', 'r') as fp:
		for line_num, row in enumerate(fp):
			searchstring = ('magnet:?xt')
			if row.find(searchstring) != -1:
				magnet_temp = row.split('magnet:')[1].split('&amp')[0]
				magnet_temp = "magnet:" + magnet_temp
				if filter_not_wanted and magnet_temp in not_wanted_magnets:
					print_warning("Skipping previously rejected magnet: " + magnet_temp[:50] + "...")
					continue
				print_success('Found magnet on line: ' + str(line_num))
				print_info("Magnet contents: " + magnet_temp)
				# get torrent title
				separator_title = f'<a href="{magnet_temp}&amp;dn='
				torrent_title = row.split(separator_title)[1].split('&amp')[0]
				# danger filter check
				is_danger = False
				if filter_danger and check_danger(torrent_title):
					if hands_on_mode:
						print_error(f"[DANGER] {torrent_title} - CONTINUE? (y/n)")
						choice = input_blue("Override danger filter? y/n: ").strip().lower()
						if choice not in ('y', 'yes'):
							not_add.append(magnet_temp)
							continue
						is_danger = True
					else:
						print_warning(f"Skipping danger-filtered torrent: {torrent_title}")
						not_add.append(magnet_temp)
						continue
				# copyright filter check
				if filter_copyright and check_copyright(torrent_title):
					print_warning(f"Skipping copyrighted torrent: {torrent_title}")
					not_add.append(magnet_temp)
					continue
				# parse size and peers from row
				torrent_size_gb = parse_size_from_row(row)
				seeders, leechers = parse_peers(row)
				size_str = f"{torrent_size_gb:.2f} GB" if torrent_size_gb else "unknown"
				seed_str = str(seeders) if seeders is not None else "?"
				leech_str = str(leechers) if leechers is not None else "?"
				# skip if no seeders
				if seeders is not None and seeders == 0:
					print_warning(f"Skipping torrent with no seeders: {torrent_title}")
					not_add.append(magnet_temp)
					continue
				# disk limit check
				if filter_disk_limit and torrent_size_gb is not None:
					if not check_disk_limit(torrent_size_gb):
						print_warning(f"Skipping torrent (exceeds disk limit): {torrent_title} ({size_str})")
						not_add.append(magnet_temp)
						continue
				print_info(f"Torrent title: {torrent_title}")
				print_info(f"  Size: {size_str} | Seeders: {seed_str} | Leechers: {leech_str}")
				magnets.append(magnet_temp)
				titles.append(torrent_title)
				sizes.append(size_str)
				danger_flags.append(is_danger)
	if not titles:
		print_warning("No magnets found on this page.")
		return
	# add-all mode or interactive selection
	if add_all_mode:
		print_success(f"Adding all {len(magnets)} magnet(s) from this page.")
		for i, magnet in enumerate(magnets):
			to_add.append(magnet)
			current_selection_sizes.append(sizes[i])
	else:
		for i, title in enumerate(titles):
			choice = ""
			print(f"--> TORRENT TITLE: {title}")
			print(f"    Size: {sizes[i]}")
			if danger_flags[i]:
				print_error("    [DANGER FLAGGED - hands-on override]")
			while choice.lower() not in ('y', 'n'):
				choice = input_blue("Add torrent y/n: ")
				if choice.lower() not in ('y', 'n'):
					print_error("Input only y or n !!!")
			if choice.lower() == 'y':
				print_success("Adding torrent.")
				to_add.append(magnets[i])
				current_selection_sizes.append(sizes[i])
			else:
				print_warning("Not adding torrent.")
				not_add.append(magnets[i])
	# ask about next page
	next_page = input_blue("View next page? y/n: ")
	while next_page.lower() not in ('y', 'n'):
		next_page = input_blue("View next page? y/n: ")
	if next_page.lower() == 'y':
		torrent_number += limit
		import random
		wait_time = random.randint(min_waittime, max_waittime)
		print_info(f"Waiting {wait_time} seconds before next page...")
		time.sleep(wait_time)
		magnets_from_page()
	else:
		add_to_i2psnark()
# --------------> getting torrent links (not magnet links)
# craft URL: postman_url + all the options + page num
# get one page of results
# input torrent links from file into table
# ask user about each one (maybe implement something SQL-esq later on, for example - exclude certain keywords)
def extract_nonce(page_html):
	try:
		for line in page_html.split('\n'):
			if 'name="nonce"' in line and '_post' in page_html:
				nonce = line.split('name="nonce" value="', 1)[1].split('"', 1)[0]
				return nonce
	except (IndexError, ValueError):
		pass
	raise RuntimeError("Failed to extract nonce from i2psnark page")

def add_magnet_to_i2psnark(magnet, nonce):
	multipart = {
		"nonce": nonce,
		"action": "Add",
		"nofilter_newURL": magnet,
		"nofilter_newDir": "",
	}
	post_url = I2PSNARK_URL + "_post"
	try:
		response = requests.post(post_url, data=multipart, timeout=30)
		if response.status_code == 200:
			return True
		else:
			print_error(f"HTTP {response.status_code}")
			return False
	except requests.RequestException as e:
		print_error(f"{e}")
		return False

def add_to_i2psnark():
	print_info("---> Preparing to add torrents to i2psnark...")
	selected_file = 'selected_magnets.txt'
	try:
		with open(selected_file, 'r') as f:
			magnets = [line.strip() for line in f.readlines() if line.strip()]
	except FileNotFoundError:
		print_error(f"{selected_file} not found. Run the crawler first.")
		return
	if not magnets:
		print_warning("No magnets found in file.")
		return
	print_info(f"Found {len(magnets)} magnet(s) to add:")
	for i, magnet in enumerate(magnets):
		print_info(f"  {i+1}. {magnet[:60]}...")
	confirm = input_blue(f"\nProceed? ({len(magnets)} torrent(s)): ").strip().lower()
	if confirm != 'y' and confirm != 'yes':
		print_warning("Aborted.")
		return
	print_info("Connecting to i2psnark...")
	try:
		response = requests.get(I2PSNARK_URL, timeout=30)
		response.raise_for_status()
	except requests.RequestException as e:
		print_error(f"Cannot reach i2psnark at {I2PSNARK_URL}")
		print_error(f"{e}")
		return
	try:
		nonce = extract_nonce(response.text)
	except RuntimeError as e:
		print_error(f"{e}")
		return
	added = 0
	failed = 0
	for i, magnet in enumerate(magnets):
		print_info(f"Adding {i+1}/{len(magnets)}...")
		if add_magnet_to_i2psnark(magnet, nonce):
			print_success(f"Added: {magnet[:50]}...")
			added += 1
		else:
			failed += 1
	print_info(f"\nDone: {added} added, {failed} failed")
	if not_add:
		existing = set(not_wanted_magnets)
		with open(NOT_WANTED_FILE, 'a') as f:
			for magnet in not_add:
				if magnet not in existing:
					f.write(magnet + '\n')
					existing.add(magnet)
		print_info(f"Saved {len(not_add)} rejected magnet(s) to {NOT_WANTED_FILE}")
	# /////////// MAIN FUNCTION /////////////
if __name__ == "__main__":
	greet()

	get_user_input()
	# some networking calls here
	authenticate_form_token()
	magnets_from_page()
	add_to_i2psnark()

	# program closure
	goodbye()
	sys.exit()
