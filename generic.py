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
	if datetime.now().hour > 12:
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
	
	d_consider = d_consider.replace(hour=13, minute=0, second=0, microsecond=0)
	return d_consider

def get_soup(dummy=False):
	
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
	url += 'fs_view?Totals' # @todo separate view
	
	if dummy:
		from dummy_data import dummy_xml
		soup = BeautifulSoup(dummy_xml, "html5lib")
		print('I\'m a dummy')
	else:
		soup = BeautifulSoup(requests.get(url).text, "html5lib")
	
	return soup

def status(soup):
	for status in soup.find_all('fs_response'):
		req_status = status.get('status')
		req_status = req_status + ' ' + status.get('timestamp')
		add_to_output(req_status + '\n')

def output_output(as_text=False):
	global output
	if as_text:
		return output
	else:
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