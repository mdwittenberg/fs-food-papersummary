import urllib
import requests
import collections
from datetime import timedelta, date, datetime

# Soup http://omz-software.com/pythonista/docs/ios/beautifulsoup_guide.html

fs_api_key = ''
form_id = ''
d_consider = datetime.now()
d = ''
soup = ''
output = ''
locations = {'210W': 0, 'CTO': 0, 'PSQ': 0, 'Spring': 0, 'Met': 0}

form_dic = {'sup': {'loc': '71',
	'org_ref': '',
	'type': '292',
	'total': '249',
	'speed': '73',
	'comment': '74'},
	'fp': {'loc': '247',
	'org_ref': '231',
	'type': '229',
	'total': '226',
	'speed': '73',
	'comment': '74'}}

def add_to_output(input=''):
	
	global output
	output = output + input + '\n'

def meta_extract(s, meta_id):
	s = str(s)
	find = '<meta id="' + meta_id + '"/>'
	offset = len(s) - s.find(find) - len(find)
	return s[-offset:].splitlines()[0].strip()

def get_form_info():
	
	import os
	global fs_api_key, form_id
	loc_here = os.path.join(os.getcwd(), os.path.dirname(__file__))
	loc_here = os.path.realpath(loc_here)
	loc_file = os.path.join(loc_here + '/170210 FS', '170211 fs_api_key.txt')
	file = open(loc_file, 'r')
	file_contents = file.readlines()
	fs_api_key = file_contents[0].rstrip()
	form_id = file_contents[1].rstrip()
	file.close()

def decide_d():
	
	global d
	global d_consider
	if datetime.now().hour > 11:
		d_consider = datetime.now() + timedelta(days=1)
	else:
		d_consider = datetime.now()
	
	if date.weekday(d_consider) == 0:
		days_back = 3
	elif date.weekday(d_consider) == 6:
		days_back = 2
	else:
		days_back = 1
		
	d_consider = d_consider - timedelta(days=days_back)
	
	d_consider = d_consider.replace(hour=11, minute=0, second=0, microsecond=0)

def get_soup():
	
	from bs4 import BeautifulSoup
	
	global d, soup
	d = d_consider.strftime('%Y-%m-%d')
	d = urllib.parse.urlencode({'fs_min_date': d})
	api_key = urllib.parse.urlencode({'fs_api_key': fs_api_key})
	
	url = 'https://fs19.formsite.com/api/users/kigokitchen/forms/'
	url += form_id + '/results?'
	url += api_key + '&'
	url += d 
	url += '&fs_limit=100&'
	url += 'fs_view?Totals'
	
	soup = BeautifulSoup(requests.get(url).text, "html5lib")

def round_up_results():
	
	global locations
	global d_consider
	
	for status in soup.find_all('fs_response'):
		req_status = status.get('status')
		req_status = req_status + ' ' + status.get('timestamp')
		add_to_output(req_status + '\n')
	
	d_simple = d_consider.strftime('%y%m%d %a %I:%M %p')
	add_to_output('## Results from ' + d_simple + '\n')
	
	results = []
	
	for ref in soup.find_all('result'):
		doo = meta_extract(str(ref),'date_finish')
		doo = datetime.strptime(doo, '%Y-%m-%d %H:%M:%S')
		if doo < d_consider:
			continue
		results.append(ref)
	
	results.reverse()
	
	for ref in results:
		for type in ref.find_all('item', id='229'):
			t = type.get_text()
			if t == '\nCredit\n':
				for org_ref in ref.find_all('item', id='231'):
					for string in org_ref.stripped_strings:
						add_to_output('Ref#' + string)
			else:
				add_to_output('Ref#'+(ref.get('id')))
		doo = meta_extract(str(ref),'date_finish')
		doo = datetime.strptime(doo, '%Y-%m-%d %H:%M:%S')
		add_to_output(doo.strftime('%y%m%d %I:%M %p'))
		valueprefix = ''
		negpos = 1
		for loc in ref.find_all('item', id='247'):
			for string in loc.stripped_strings:
				add_to_output(string)
				location = string
		for type in ref.find_all('item', id='229'):
			t = type.get_text()
			if t == '\nCredit\n':
				valueprefix = 'CREDIT FOR ' + valueprefix
				negpos = -1
		for total in ref.find_all('item', id='226'):
			for string in total.stripped_strings:
				add_to_output(valueprefix + '${:,.2f}'.format(float(string)))
				if location in locations:
					locations[location] += float(string)*negpos
				else:
					locations[location] = float(string)*negpos
		for speed in ref.find_all('item', id='73'):
			for string in speed.stripped_strings:
				if string != 'Normal delivery':
					add_to_output(string)
		for comment in ref.find_all('item', id='74'):
			for string in comment.stripped_strings:
				if string != 'n/a':
					add_to_output(string)
		add_to_output()
	
	locations = collections.OrderedDict(sorted(locations.items()))
	
	add_to_output('## TOTALS\n')
	for store, total in locations.items():
		add_to_output('{0:7} ${1:8,.2f}'.format(store, total))

def output_output():
	global output
	try:
		import clipboard
		if clipboard.get() != 'iamfromworkflow':
			import console
			console.clear()
			print(output)
		else:
			import webbrowser
			clipboard.set(output)
			webbrowser.open('workflow://')
	except ModuleNotFoundError as err:
		output = '\n' + output
		print(output)

get_form_info()
decide_d()
get_soup()
round_up_results()
output_output()