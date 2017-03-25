from generic import *
from delivery import *

dummy_data = True

get_form_info()
d_consider = decide_d()

soup = get_soup(dummy_data)
status(soup)
round_up_results(soup, d_consider, locations)

output_output()

if dummy_data:
	print('[dummy data]')