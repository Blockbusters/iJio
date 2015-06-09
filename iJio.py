import cgi
from google.appengine.api import users
import urllib
import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('iJio.html')
        self.response.out.write(template.render())

class Login(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()

        if user:
		# Successful Login
            	self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
            	self.response.write('Hello, ' + user.nickname())
        else:
		# Request for login
            	self.redirect(users.create_login_url(self.request.uri))

GUESTBOOK_MAIN_HTML = """\
<html>
  <body>
    <form action="/gbw" method="post">
    	<div><textarea name="content" rows="3" cols="60"></textarea></div>
	<p>
      <input type="submit" value="Sign Guestbook">	  
    </form>
	<form action="/">
		<input type="submit" value="Back">
	</form>
  </body>
</html>
"""

class Guestbook(webapp2.RequestHandler):
	def get(self):
		self.response.write(GUESTBOOK_MAIN_HTML)

class GuestbookWrite(webapp2.RequestHandler):
	def post(self):
		self.response.write("<html><body>Test message: ")
		self.response.write(cgi.escape(self.request.get('content')))
		self.response.write("<p><form action=\"/\"><input type=\"submit\" value=\"Back\"></form>")
		self.response.write("</body></html>")
	
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', Login),
    ('/gb', Guestbook),
    ('/gbw', GuestbookWrite),
], debug=True)
