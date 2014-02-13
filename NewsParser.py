from bs4 import BeautifulSoup
from urlparse import urlparse
import urllib2
import re
import sys
import subprocess
	
def getWebsiteName(targetURL):
	'''
	Grab the site name
	'''
	#Slice up url with regex and grab the domain name.
	regex = '([a-zA-Z0-9-]*)\.(com|edu|net|org|us)'
	return re.search(regex, targetURL).group(1)
	
def getArticleHTML(targetURL):
	'''
	Returns the HTML for a page as a string
	'''
	targetHTML = urllib2.urlopen(targetURL).read()
	return targetHTML

def titleHTML(title):
	'''
	Adds preferred tags for titles.
	'''
	return '<p><strong><em>' + str(title).encode('utf-8') + '</em></strong></p>'

def authorHTML(author):
	'''
	Adds HTML for authors.
	'''
	return '<em>' + author.encode('utf-8') + '</em>'

def sanitizeYAML(text):
	'''
	Escapes YAML characters and removes newlines.
	'''
	return text.replace('\\','').replace('"','\\"').replace('\n','')

class ArticleParser:
	'''
	Parses news articles into Tumblr image posts
	Members:
	    (string) template:
	        The template used to generate the files.
	    (string) outFile:
	    	Name of the output file
	'''
	def __init__(self, template, outFile='out.txt'):
		'''
		Constructor
		Args:
			(string) template:
				The template file to use.
		'''
		f = open(template, 'r')
		self.template = f.read()
		self.outFile = outFile
		f.close()
		
	def io9Parser(self, targetURL):
		'''
		Parses an io9 article
		'''
		#Image regular expression
		imgRegex = 'data-asset-url="(.*?)"'
		imgRegex = re.compile(imgRegex)
	
		targetHTML = getArticleHTML(targetURL)
	
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
		body = titleHTML(title) + '</br>' + authorHTML(author) + body
		body = sanitizeYAML(body)
	
		output = self.template % {'image':image, 'url':targetURL, 
						          'body':body, 'tags':tags.encode('utf-8')}
		#Return formatted string
		return output
	
	def sciencedailyParser(self, targetURL):
		'''
		Process ScienceDaily articles
		'''
		#Create bs4 object
		newsDocument = BeautifulSoup(getArticleHTML(targetURL))
		
		title = newsDocument.title
		image = newsDocument.find('meta', id='og_image')['content']
		author = newsDocument.find(id='source').text
		#Process tags
		tags = newsDocument.find('meta', id='metakeywords')['content'].split(';')
		tags = 'Science, ' + ','.join(tags)
		#Build body
		body = ''
		body = titleHTML(title) + '</br>' + authorHTML(author) + body
		
		for paragraph in newsDocument.select('#story p')[0:5]:
			body = body + str(paragraph)
		body = sanitizeYAML(body)
		
		output = self.template % {'image':image, 'url':targetURL, 
						          'body':body, 'tags':tags.encode('utf-8')}
		return output
		
	def generatePost(self, targetURL):
		websiteName = getWebsiteName(targetURL)
		
		#Fetch the appropriate parser.
		parser = getattr(self, websiteName + 'Parser')
		try:
			output = parser(targetURL)
		except:
			raise ValueError("Website not recognized")
		
		outFile  = open(self.outFile, 'w')
		outFile.write(output)

if __name__ == '__main__':
	#Checks for argument in command line
	try:
		targetURL = sys.argv[1]
	except:
		print('Usage: NewsParser.py -url')
		exit()
	
	parser = ArticleParser('imageTemplate.txt')
	
	parser.generatePost(targetURL)
	subprocess.call("tumblr post out.txt --host=http://alex-does-science.tumblr.com", shell=True)