import cgi
import urllib
import webapp2
import jinja2
import os
import time
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class UTC0800(datetime.tzinfo):
    """tzinfo derived concrete class named "+0800" with offset of 28800"""
    # can be configured here
    _offset = datetime.timedelta(seconds = 28800)
    _dst = datetime.timedelta(0)
    _name = "+0800"
    def utcoffset(self, dt):
        return self.__class__._offset
    def dst(self, dt):
        return self.__class__._dst
    def tzname(self, dt):
        return self.__class__._name
tz = UTC0800()
       
class Month(ndb.Model):
    year = ndb.IntegerProperty(indexed=False)
    month = ndb.IntegerProperty(indexed=False)
    # 0 means busy, 1 is free.
    w1 = ndb.IntegerProperty(indexed=False) # stores 32 bits: (Morn/Aft/Eve/Night)
    w2 = ndb.IntegerProperty(indexed=False)
    w3 = ndb.IntegerProperty(indexed=False)
    w4 = ndb.IntegerProperty(indexed=False)
        
class User(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    friendList = ndb.StringProperty(repeated=True, indexed=False) # list of user id
    eventList = ndb.IntegerProperty(repeated=True, indexed=False) # list of event id
    friendRequestList = ndb.StringProperty(repeated=True, indexed=False) # list of user id incoming friends requests
    friendRequestingList = ndb.StringProperty(repeated=True, indexed=False) # list of user id outgoing friend requests
    calendar = ndb.StructuredProperty(Month, repeated = True) # Personal Calendar of months

class Event(ndb.Model):
    eventID = ndb.IntegerProperty() #query count to associate ID
    #datetime = ndb.ComputedProperty()
    invitedUsers = ndb.StringProperty(repeated=True, indexed=False)
    acceptedUsers = ndb.StringProperty(repeated=True, indexed=False)
    rejectedUsers = ndb.StringProperty(repeated=True, indexed=False)
    
    #User Inputs
    name = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    dateRange = ndb.IntegerProperty(repeated=True) # pair of start and end date

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.redirect("/login")

#TODO: eventually shift to their individual html files to pretty up.        
LOGOUT_OPTION = """\
	<form action="/logout">
        <input type="submit" value="Logout">
	</form>
"""
NEWLINE = """\
<p></p>
"""
BACKHOME = """\
    <button method="get" onClick="location.href='/home' ">Back to Home Page</button>
"""
BACKSEARCH = """\
    <button method="get" onClick="location.href='/search' ">Back to Search</button>
"""
 
class LoginPage(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()

        if user:
		# Successful Login
            qry = User.query(User.email == user.email())
            # New User
            if qry.count() == 0:
                self.redirect("/register")
            # Returning User
            else:
            	self.redirect("/home")
        else:
		# Request for login
            self.redirect(users.create_login_url(self.request.uri))

class Register(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qry = User.query(User.email == user.email())
        if qry.count() > 0:
            self.redirect("/home")
        else:
            calendar = []
            initweek = 1111111111111111111111111111
            for i in range(12):
                month = Month(w1 = 1111111111111111111111111111, w2 = 1111111111111111111111111111, w3 = 1111111111111111111111111111, w4 = 1111111111111111111111111111)
            temp = user.email()
            newuser = User(name = temp.title(), email = temp.lower(), friendList = [], eventList = [])
            userkey = newuser.put()
            template = jinja_environment.get_template('register.html')
            self.response.out.write(template.render())
			
class LogOut(webapp2.RequestHandler):
	def get(self):
		self.redirect(users.create_logout_url('/'))

class HomePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qry = User.query(User.email == user.email())
        name = qry.get().name
        numFriends = str(len(qry.get().friendRequestList))
        template = jinja_environment.get_template('home.html')
        self.response.out.write(template.render({"name":name,"counter":numFriends}))
		
#TODO: Is it possible to shove all login required functionality into one python file where we can declare global user and qry?
#NOTE: sanitize inputs: ensure all names are in Proper Form and all emails are in lowercase.
#TODO: how to ensure name is not blank? my if blocks seem to crash the program lol
		
class Update(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		qry = User.query(User.email == user.email())
		tempUser = qry.get()
		tempUser.name = self.request.get('content').title()
		tempUser.put()
		time.sleep(1) # import time. Waits for 1 second so that db can be updated with new name.
		self.redirect("/login")

class ManageFriends(webapp2.RequestHandler):
    def get(self):        
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email())
        friendListPrint = []
        count = 1
        for friend in qrySelf.get().friendList:
            qryFriend = User.query(User.email == friend).get()
            friendListPrint.append(str(count) + ") Name: " + qryFriend.name + ", Email: " + friend + "<br>")
            count += 1
        template = jinja_environment.get_template('friendlist.html')
        self.response.out.write(template.render({"printList" : friendListPrint}))

class ViewRequests(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email())
        if len(qrySelf.get().friendRequestList) == 0:
            self.response.write("You have no friend requests.<p>")
            self.response.write(BACKHOME)
        else:
            self.response.write("Friend Requests: <p>")
            for friend in qrySelf.get().friendRequestList:
                qryFriend = User.query(User.email == friend)
                self.response.write("Name: " + qryFriend.get().name)
                self.response.write("<br>Email: " + qryFriend.get().email)
                self.response.write("<button method=\"get\" onClick=\"location.href='/acceptFriend?value={email}'\">Accept Friend</button>".format(email = friend))
                self.response.write(NEWLINE)

class AcceptFriend(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email())
        toAdd = self.request.get('value')
        qryFriend = User.query(User.email == toAdd)
        qrySelf.get().friendRequestList.remove(toAdd)
        qryFriend.get().friendRequestingList.remove(user.email())
        qrySelf.get().friendList.append(toAdd)
        qryFriend.get().friendList.append(user.email())
        qrySelf.get().put()
        qryFriend.get().put()
        time.sleep(1)
        self.redirect("/viewRequest")
       
class Search(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('search.html')
        self.response.out.write(template.render())

class SearchResults(webapp2.RequestHandler):        
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email())
        name = self.request.get('name').title()
        qry1 = User.query(User.name == name)
        numFound1 = qry1.count()
        pair = []
        for key in qry1.iter():
            email = key.email
            case = checkAdding(email, qrySelf.get())
            pair.append([key.name, key.email, case])  
        template = jinja_environment.get_template('searchresults.html')
        self.response.out.write(template.render({"numFoundName":numFound1,"name":name, "pair":pair})) 
            
#check if person has already been added
def checkAdding(personEmail, user):
    if personEmail == user.email:
        return 1
    for i in user.friendList:
        if personEmail == i:
            return 2
    for i in user.friendRequestingList:
        if personEmail == i:
            return 3
    for i in user.friendRequestList:
        if personEmail == i:
            return 4
    return False
        
class AddFriend(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email())
        toAdd = self.request.get('value')
        qryFriend = User.query(User.email == toAdd)
        qrySelf.get().friendRequestingList.append(toAdd)
        qryFriend.get().friendRequestList.append(user.email())
        qrySelf.get().put()
        qryFriend.get().put()
        self.redirect("/search")

class ManageTimetable(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        now = datetime.datetime.now(tz)
        self.response.write("Today is " + str(now.day) + "-" + str(now.month) + "-" + str(now.year))
        self.response.write("<p> The time now is " + str(now.hour) + ":" + str(now.minute))
        month = qrySelf.calendar
               
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', LoginPage),
    ('/home', HomePage),
    ('/register', Register),
    ('/logout', LogOut),
    ('/update', Update),
    ('/search', Search),
    ('/searchresults', SearchResults),
    ('/addfriend', AddFriend),
    ('/manage', ManageFriends),
    ('/viewRequest', ViewRequests),
    ('/acceptFriend', AcceptFriend),
    ('/managetimetable', ManageTimetable),
], debug=True)


#TODO: DECIDE ON CALENDAR STRUCTURE
'''
    class Activity(ndb.Model):
    date = ndb.DateProperty()
    time = ndb.StringProperty()  
    availability = ndb.BooleanProperty() # true = occupied, false = free
    
class BitCalendar(ndb.Model):
'''