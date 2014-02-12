from bs4 import BeautifulSoup
from urlparse import urlparse
import urllib2
import re
import sys
import subprocess

def io9Parser(targetURL):
	#Read in file template
	template = open('imageTemplate.txt', 'r')
	output   = template.read()
	
	imgRegex = 'data-asset-url="(.*?)"'
	imgRegex = re.compile(imgRegex)
	
	targetHTML = urllib2.urlopen(targetURL).read()
	
	#Turn into BeautifulSoup object for use
	newsDocument = BeautifulSoup(targetHTML)
	
	#Get title
	title = newsDocument.title
	
	#Get image
	image = re.search(imgRegex, targetHTML).group(1)
	
	#Get a body
	body = ''
	paragraphs = newsDocument.select('div.post-content p')
	for i in range(1,5):
		body += str(paragraphs[i])
	
	#Get author
	author = newsDocument.find('meta', attrs={'name':'author'})['content']
	
	#Grab tags
	tags = []
	for tag in newsDocument.select('.taglist li'):
		tags.append(tag.text)
	tags = ','.join(tags)
	#Format the template and output
	#Escape and process html for yaml
	body = re.sub('<p.*?>','<p>', body)
	body = '<p><strong><em>' + str(title) + '</em></strong></p>' + '</br>' + \
	       '<em>' + author.encode('utf-8') + '</em>' + body
	body = body.replace('\\','').replace('"','\\"').replace('\n','')
	
	output = output % {'image':image, 'url':targetURL, 
	                   'body':body, 'tags':tags.encode('utf-8')}
	#Return formatted string
	return output
	
def generatePost(targetURL):
	webdomain = (urlparse(targetURL))[1]
	if webdomain == 'io9.com':
		output = io9Parser(targetURL)
	else:
		raise ValueError("Website not recognized")
		
	outFile  = open('out.txt', 'w')
	outFile.write(output)

if __name__ == '__main__':
	#Checks for argument in command line
	try:
		targetURL = sys.argv[1]
	except:
		print('Usage: NewsParser.py -url')
		exit()

	generatePost(targetURL)
	subprocess.call("tumblr post out.txt --host=http://alex-does-science.tumblr.com", shell=True)