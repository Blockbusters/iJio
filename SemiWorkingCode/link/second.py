import webapp2

BACKHTML = """\
<html>
	<body>
		<p><a href="/">Back to Main Page</a>
	</body>
</html>
"""

class SecondPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Second Page")
        self.response.write(BACKHTML)

app = webapp2.WSGIApplication([
    ('/sec', SecondPage),
], debug=True)
