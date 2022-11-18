#!/usr/bin/python3

import sys, getopt, requests, os, shutil
import time, datetime
from bs4 import BeautifulSoup
import mysql.connector

DATABASE_HOST = "localhost"
DATABASE_NAME = "lmd"
DATABASE_USER = "root"
DATABASE_PASS = "root"

def main():
	try:
		operators, arguments = getopt.getopt(sys.argv[1:], "chdu:y:", ["help", "debug", "username", "year", "clear-cache"])
	except getopt.GetoptError as err:
		help()
		sys.exit(2)

	username = None
	year = None
 
	global debug
	debug = False

	for operator, argument in operators:
		if operator in ("-h", "--help"):
			help()
			sys.exit()
		elif operator in ("-d", "--debug"):
			debug = True
		elif operator in ("-c", "--clear-cache"):
			clear_cache()
		elif operator in ("-u", "--username"):
			username = argument
			if not username:
				print_error("Username is empty")
		elif operator in ("-y", "--year"):
			year = argument
			if not year:
				print_error("Year is empty")
		else:
			assert False, "unhandled option"

	dataset = []
	start_url = "https://www.last.fm/user/{}/library?from={}-01-01&rangetype=year".format(username, year)
	dataset = parse_overview_page(start_url, username, dataset)
	insert_datasets(dataset)

def parse_overview_page(url, username, dataset):
	
	response = get_response(url)
	soup = BeautifulSoup(response, 'html.parser')
	tracks = soup.find_all(class_='chartlist-row')
	for track in tracks:   
		title = track.find(class_='chartlist-name').find('a').text
		artist = track.find(class_='chartlist-artist').find('a')
		album = track.find(class_='chartlist-image').find('img')['alt']

		genre_link = "https://www.last.fm{}/+tags".format(track.find(class_='chartlist-name').find('a')['href'])
		genre = parse_genre(genre_link)

		date = track.find(class_='chartlist-timestamp').find('span')['title']
		datepieces = date.split(" ")
		timepieces = convert_to_24(datepieces[4]).split(":")
		datestamp = time.mktime((int(datepieces[3][0:4]), int(time.strptime(datepieces[2],'%b').tm_mon), int(datepieces[1]),int(timepieces[0]),int(timepieces[1]),0,0,0,0))
		date = datetime.datetime.fromtimestamp(datestamp).strftime('%Y-%m-%d %H:%M:%S')

		set = {
			'artist': artist.text,
			'album': album,
			'title': title,
			'genre': genre,
			'date': date,
		}
		dataset.append(set)

	next_page = soup.find(class_="pagination-next")
	if next_page:
		next_url = "https://www.last.fm/user/{}/library{}".format(username, next_page.find("a")['href'])
		parse_overview_page(next_url, username, dataset)
	else:
		return dataset

	return dataset

def parse_genre(genre_link):
	genre_list = []
	response = get_response(genre_link)
	soup = BeautifulSoup(response, 'html.parser')
	genres = soup.find_all(class_='big-tags-item-wrap')
	for genre in genres:
		genre_list.append(genre.find(class_='link-block-target').text)

	return genre_list

def get_response(url):

	cached_url = "".join(c for c in url if c.isalnum())
	cached_file = "./cache/{}.html".format(cached_url)
	if os.path.exists(cached_file):
		if debug:
			print("DEBUG: Parsing from CACHE {}".format(cached_file))

		file = open(cached_file, 'r')
		content = file.read()
		file.close()
		return content
	else:
		if debug:
			print("DEBUG: Parsing {}".format(url))
		
		with requests.get(url) as response:
			if response.status_code != 200:
				print_error("Something went wrong with requesting URL.")

		file = open(cached_file, "w")
		file.write(response.text)
		file.close()

		return response.text

def convert_to_24(timestring):	
	if timestring[1] == ":":
		timestring = "0{}".format(timestring)

	if timestring[-2:] == "am":
		if timestring[:2] == "12":
			timestring = "00{}".format(timestring[2:])
			
	if timestring[-2:] == "pm":
		if timestring[:2] != "12":
			timestring = "{}:{}".format((int(timestring[:2]) + 12), timestring[3:])
	
	return "{}:00".format(timestring[:-2])

def insert_datasets(datasets):

	connection = mysql.connector.connect(user=DATABASE_USER, password=DATABASE_PASS, host=DATABASE_HOST, database=DATABASE_NAME)

	for set in datasets:

		if debug:
			print("Importing track {}".format(set['title']))

		cursor = connection.cursor(buffered=True)

		query = "INSERT INTO plays (date, artist, album, track) VALUES (%(date)s, %(artist)s, %(album)s, %(track)s)"
		values = {'date': set['date'], 'artist': set['artist'], 'album': set['album'], 'track': set['title']}
		cursor.execute(query, values)
		play_id = cursor.lastrowid
  
		for genre_name in set['genre']:
			check_genre_query = "SELECT id, name FROM `genre` WHERE `name` = %(name)s"
			cursor.execute(check_genre_query, {'name': genre_name})
			genre = cursor.fetchone()
			if not genre:
				query = "INSERT INTO genre (name) VALUES (%(name)s)"
				values = {'name': genre_name}
				cursor.execute(query, values)
    
				genre_id = cursor.lastrowid
			else:
				genre_id = genre[0]

			query = "INSERT INTO `play_genre` SET `play_id` = %(play_id)s, `genre_id` = %(genre_id)s"
			values = {'play_id': play_id, 'genre_id': genre_id}
			cursor.execute(query, values)

		connection.commit()

	connection.close()

def clear_cache():
	for filename in os.listdir("./cache/"):
		if filename == ".gitkeep":
			continue

		file_path = os.path.join("./cache/", filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except Exception as e:
			print('Failed to delete %s. Reason: %s' % (file_path, e))

def help():
	print("Usage: ./scrap-lastfm.py -u <username> -y <year>")

def print_error(errorMessage):
	message = "\033[1mError:\033[0m {}".format(errorMessage)
	print(message)
	help()
	sys.exit()

if __name__ == "__main__":
	main()