from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
import re
import time
 

# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):


	# This is a function that HTMLParser normally has
	# but we are adding some functionality to it
	def handle_starttag(self, tag, attrs):
		# We are looking for the begining of a link. Links normally look
		# like <a href="www.someurl.com"></a>
		if tag == 'a':
			for (key, value) in attrs:
				if key == 'href':
					# We are grabbing the new URL. We are also adding the
					# base URL to it. For example:
					# www.netinstructions.com is the base and
					# somepage.html is the new URL (a relative URL)
					#
					# We combine a relative URL with the base URL to create
					# an absolute URL like:
					# www.netinstructions.com/somepage.html
					newUrl = parse.urljoin(self.baseUrl, value)
					# And add it to our colection of links:
					self.links = self.links + [newUrl]

	# This is a new function that we are creating to get links
	# that our spider() function will call
	def getLinks(self, url, band):
		self.links = []
		# Remember the base URL which will be important when creating
		# absolute URLs
		self.baseUrl = url
		# Use the urlopen function from the standard Python 3 library
		response = urlopen(url)
		# Make sure that we are looking at HTML and not other things that
		# are floating around on the internet (such as
		# JavaScript files, CSS, or .PDFs for example)
		if response.getheader('Content-Type')=='text/html':
			htmlBytes = response.read()
			# Note that feed() handles Strings well, but not bytes
			# (A change from Python 2.x to Python 3.x)
			htmlString = htmlBytes.decode("utf-8")
			self.feed(htmlString)

			#TODO: filter links (only songs)
			self.links = [link for link in self.links if 'lyrics/'+band in link]
			return self.links
		else:
			return []

	def getLyrics(self, url):
		#print(url)
		
		response = urlopen(url)
		# Make sure that we are looking at HTML and not other things that
		# are floating around on the internet (such as
		# JavaScript files, CSS, or .PDFs for example)
		if response.getheader('Content-Type')=='text/html':
			htmlBytes = response.read()
			# Note that feed() handles Strings well, but not bytes
			# (A change from Python 2.x to Python 3.x)
			htmlString = htmlBytes.decode("utf-8")
			title = htmlString[htmlString.index('"div-share"')+17:]
			title = title[:title.index('"')]
			htmlString = htmlString[htmlString.index("<div>")+5:]
			htmlString = htmlString[:htmlString.index("</div>")]
			htmlString = re.compile(r'<[^>]+>').sub('', htmlString)

			self.feed(htmlString)
			
			return title, htmlString
		else:
			return title, ""


def spider(url):  

	parser = LinkParser()
	band = url[url.rfind('/')+1:-5]
	links = parser.getLinks(url, band)
	file = open(band+".txt", "w")

	while len(links) > 0:
		# Start from the beginning of our collection of pages to visit:
		try:
			print(links[0])
			title, data = parser.getLyrics(links[0])
			file.write(title)
			file.write(data)
			links = links[1:]
			time.sleep(1)
			return
			
		except:
			print(" **Failed!**")
			file.close()

	file.close()

spider('https://www.azlyrics.com/p/pearljam.html')