import webapp2
import jinja2
import os
import time

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class ThirdPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("3rd page")
        answer = self.request.get('userAns')
        if answer == "5":
            mark = "Correct"
        elif answer == "":
            mark = " "
        else:
            mark = "Wrong"
        template = jinja_environment.get_template('third.html')
        self.response.out.write(template.render({'answer':answer,'mark':mark}))
		
app = webapp2.WSGIApplication([
    ('/third', ThirdPage),
], debug=True)
