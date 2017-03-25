from generic import *

locations = {'210W': 0, 'CTO': 0, 'Kent': 0, 'Spring': 0}

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

def round_up_results(soup, d_consider, locations):
	
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