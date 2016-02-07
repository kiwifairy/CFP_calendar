from urllib import request
import re
import csv
import datetime
from bs4 import BeautifulSoup

#topics = ["healthcare", "health","game"]
med_topics = ['health', 'medicine', 'medical', 'healthcare', 'ehealth','e-health','health%20informatics','bioinformatics', 'biotechnology', 'biology', 'biomedical%20engineering', 'biomedical', 'life%20sciences', 'molecular%20biology','cognitive%20science','neuroscience']
tech_topics = ['HCI', 'human-computer interaction', 'human%20computer%20interaction','virtual%20reality', 'games	', 'visualization', 'entrepreneurship', 'augmented%20reality', 'interaction']
art_topics = ['humanities', 'design','interdisciplinary', 'art', 'film']
urlpart1 = "http://www.wikicfp.com/cfp/call?conference="
prefix = 'http://www.wikicfp.com'

def get_list(topic):
	#given a topic, get all the list of conf link
	nextPage = True
	conf_link = []
	html = request.urlopen(urlpart1 + topic).read()
	while nextPage:
		soup = BeautifulSoup(html,"lxml")
		content = soup.find("div", class_="contsec")
		rows = content.table.find_all('tr')
		for row in rows:
			cols2 = row.find_all('td')
			for ele in cols2:
				if ele.find_all(text=re.compile("Expired")):
					nextPage = False
				if ele.a and 'facebook' not in ele.a["href"] and 'page' not in ele.a["href"]:
					conf_link.append(ele.a["href"])
		if nextPage:
			url = prefix + soup.find(text=re.compile("next")).parent['href']
			html = request.urlopen(url).read()
	return conf_link

def get_conf_info(url):
# def get_conf_info():
	info = []
	html = request.urlopen(prefix + url).read() #open('conf2.html').read()#
	soup = BeautifulSoup(html,'lxml')
	theaders = soup.find_all('th')
	deadline = None
	subject = ''
	link = ''
	description = ''
	try:
		subject = soup.find('span', {'property': 'v:description'}).text
		link = soup.find(text=re.compile("Link:")).parent.a['href']
		description = soup.find("div", class_="cfp").text.strip()
	except:
		pass
	for th in theaders:
		info = th.next_sibling.next_sibling.text.strip()
		header = th.text
		if 'Where' in header:
			location = '" '+info +' "'
		elif 'When' in header:
			conf_time = info
		else:
			try:
				dt = datetime.datetime.strptime(info.replace(',',''), '%b %d %Y')
				if dt < datetime.datetime.today() :
					return None
				if (deadline is None) or (dt < deadline):
					deadline = dt
			except:
				pass
	description = '"  Link: '+link +' \n '+ description + ' "'
	try:
		deadline_string =  '{0}/{1}/{2}'.format(deadline.month, deadline.day, deadline.year)
	except:
		deadline = datetime.datetime.strptime('Dec 31 2016', '%b %d %Y')
		deadline_string = '{0}/{1}/{2}'.format(deadline.month, deadline.day, deadline.year)
	info = [subject, deadline_string, deadline_string, 'True', description, location]
	return info


def main():
	conf_data_list = []
	conf_link = set()
	for topic in med_topics:
		conf_link |= set(get_list(topic))
	for link in conf_link:
		one_conf_data = get_conf_info(link)
		if one_conf_data is not None:
			print('')
			print(one_conf_data[4])
			print(one_conf_data[0])
			useful = input().lower() 
			if 'y' in useful:
				conf_data_list.append(one_conf_data)
	filename = 'medical.csv'
	with open(filename, 'w') as outcsv:
	    fieldnames = ['Subject','Start Date','End Date', 'All Day Event','Description','Location']
	    writer = csv.writer(outcsv)
	    writer.writerow(fieldnames)
	    writer.writerows(conf_data_list)

		# with open(filename, 'w') as fp:
		# 	json.dump(topic_dict, fp)


main()
