import cgi
import urllib
import webapp2
import jinja2
import os
import time
import second # code for second page
import third # code for third page

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):
    def get(self):
        result_py = 2
        apple = 3
        self.response.write("Main Page")
        template = jinja_environment.get_template('link.html')
		# template.render() require parameters in order to display python var in html files.
        self.response.out.write(template.render({'result_html':result_py, 'banana':apple}))
        self.response.write("<html><body><a href=\"/sec\">Next Page</a><p><a href=\"/third\">Third Page</a></body></html>")
	
app = webapp2.WSGIApplication([
	('/', MainPage),
	('/sec', second.SecondPage),
	('/third', third.ThirdPage),
], debug=True)
