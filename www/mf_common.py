import os

#number of headers and paragraphs: to be updated frequently
__NUM_HEADS__ = 21
__NUM_PROSE__ = 35

def get_prose(fname):
	path = os.path.join(os.path.dirname(__file__), 'prose')
	f = open(os.path.join(path, fname), 'r')
	try:
		#kludge due to python2 (grr..)
		prose = unicode(f.read(), 'utf-8')
	finally:
		f.close()
	return prose


