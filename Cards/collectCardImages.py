
import requests
from PIL import Image
from StringIO import StringIO
import os.path


suit = ['Club', 'Diamond', 'Heart', 'Spade']
face = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

url_start = 'http://www.cardplayer.com/packages/cards/Large'
my_dir = '/Users/....'

k=1
for (ind_s, s) in enumerate(suit):
	for (ind_f, f) in enumerate(face):
		url = os.path.join(url_start, s, f+'.png')
		print 'k = {0}\turl = {1}'.format(k, url),
		r = requests.get(url)
		if (r.status_code==200):
			im = Image.open(StringIO(r.content))
			im_name = 'Large-'+str(1+ind_s+4*ind_f)+'.png'
			im.save(os.path.join(my_dir, im_name))
			print "\t{0} saved as {1}".format(s+'-'+f, im_name)
		k += 1





