import cgi
import urllib
import webapp2
import jinja2
import os
import time
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class Counter(ndb.Model):
    created = ndb.BooleanProperty()
    count = ndb.IntegerProperty(indexed=False)

#Time Stuff
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
monthNow = datetime.datetime.now(tz).strftime("%m")
    
class Month(ndb.Model):
    #year = ndb.IntegerProperty(indexed=False) to be implemented someday
    month = ndb.IntegerProperty(indexed=False)
    # 0 means busy, 1 is free.
    w1 = ndb.IntegerProperty(indexed=False) # stores 31 bits: MSB + (Morn/Aft/Eve/Night) 
    w2 = ndb.IntegerProperty(indexed=False)
    w3 = ndb.IntegerProperty(indexed=False)
    w4 = ndb.IntegerProperty(indexed=False)
        
class User(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    friendList = ndb.StringProperty(repeated=True, indexed=False) # list of user id
    friendRequestList = ndb.StringProperty(repeated=True, indexed=False) # list of user id incoming friends requests
    friendRequestingList = ndb.StringProperty(repeated=True, indexed=False) # list of user id outgoing friend requests
    calendar = ndb.StructuredProperty(Month, repeated = True) # Personal Calendar of months
    eventList = ndb.IntegerProperty(repeated=True, indexed=False) # list of event id (not accepted yet)
    eventAcceptedList = ndb.IntegerProperty(repeated=True, indexed=False) # list of event ids accepted (and not over if possible)

class Event(ndb.Model):
    eventID = ndb.IntegerProperty() #query count to associate ID
    datetime = ndb.IntegerProperty()
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
        qryCounter = Counter.query(Counter.created == True)
        if qryCounter.count() == 0:
            counter = Counter(created = True, count = 1)
            counter.put()
            qryCounter = Counter.query(Counter.created == True)
        self.redirect("/login")
       
LOGOUT_OPTION = """\
	<form action="/logout">
        <input type="submit" value="Logout">
	</form>
"""
NEWLINE = """\
<p>
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


#TODO: add year to months and calendar
class Register(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qry = User.query(User.email == user.email())
        if qry.count() > 0:
            self.redirect("/home")
	else:
            tcalendar = []
            for i in range(12):
                tmonth = Month(month = i + 1, w1 = 0xFFFFFFFF, w2 = 0xFFFFFFFF, w3 = 0xFFFFFFFF, w4 = 0xFFFFFFFF)
                tcalendar.append(tmonth)
            temp = user.email()
            newuser = User(name = temp.title(), email = temp.lower(), friendList = [], eventList = [], calendar = tcalendar)
            newuser.put()
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
        numEventReq = str(len(qry.get().eventList))
        template = jinja_environment.get_template('home.html')
        self.response.out.write(template.render({"name":name,"counter":numFriends, "month":monthNow, "numEventReq":numEventReq}))
		
#TODO: Is it possible to shove all login required functionality into one python file where we can declare global user and qry?
		
class Update(webapp2.RequestHandler):
	def post(self):
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
        numRequests = len(qrySelf.get().friendRequestList)
        requestList = []
        index = False
        for friend in qrySelf.get().friendRequestList:
                qryFriend = User.query(User.email == friend)
                friendObj = []
                friendObj.append("Name: " + qryFriend.get().name + "<br>Email: " + qryFriend.get().email) #Stores text to print
                friendObj.append(friend) #Stores email so as to make use in html code
                friendObj.append(index)
                requestList.append(friendObj)
                index = not index
        template = jinja_environment.get_template('viewrequests.html')
        self.response.out.write(template.render({"counter" : numRequests, "requestList" : requestList}))
        
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

#TODO: print days, and vary num of dates.
class ManageTimetable(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        month = int(self.request.get("month"))
        monthStr = datetime.date(2015, month, 1).strftime('%B')
        userMonth = []
        userMonthObj = qrySelf.calendar[month - 1]
        #should be settled
        userMonth.append(str(bin(userMonthObj.w1)[2:]))
        userMonth.append(str(bin(userMonthObj.w2)[2:]))
        userMonth.append(str(bin(userMonthObj.w3)[2:]))
        userMonth.append(str(bin(userMonthObj.w4)[2:]))
        template = jinja_environment.get_template('timetable.html')
        self.response.out.write(template.render({"monthStr": monthStr, "userMonth": userMonth, "monthNum": month}))
        self.response.write(BACKHOME)
        
class UpdateTime(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        w1 = "0b1"
        w2 = "0b1"
        w3 = "0b1"
        w4 = "0b1"
        for i in range(1, 32):
            checked = self.request.get(str(i))
            if (checked == "on"):
                w1 += "0"
            else:
                w1 += "1"
        for i in range(32, 63):
            checked = self.request.get(str(i))
            if (checked == "on"):
                w2 += "0"
            else:
                w2 += "1"
        for i in range(63, 94):
            checked = self.request.get(str(i))
            if (checked == "on"):
                w3 += "0"
            else:
                w3 += "1"
        for i in range(94, 125):
            checked = self.request.get(str(i))
            if (checked == "on"):
                w4 += "0"
            else:
                w4 += "1"
        month = int(self.request.get("month"))
        userMonthObj = qrySelf.calendar[month - 1]
        userMonthObj.w1 = int(w1, 2)
        userMonthObj.w2 = int(w2, 2)
        userMonthObj.w3 = int(w3, 2)
        userMonthObj.w4 = int(w4, 2)
        qrySelf.put()
        time.sleep(0.5)
        self.redirect("/managetimetable?month={month}".format(month = month))

#TODO: zebra datepicker how to validate??
class CreateEvents(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        namelist = qrySelf.friendList
        friendList = []
        for friend in namelist:
            qryFriend = User.query(User.email == friend).get()
            friendList.append([qryFriend.name, friend])
        template = jinja_environment.get_template('createevents.html')
        self.response.out.write(template.render({"friendlist":friendList}))
        
class ProcessEvent(webapp2.RequestHandler):
    def post(self):
        #Get data
        user = users.get_current_user()
        invite = self.request.get('invite')
        invited = invite.split(", ")
        start = self.request.get('datestart')
        end = self.request.get('dateend')
        #dirtyfix:
        if start == "":
            start = "01/01/2015"
        if end == "":
            end = "31/12/2015"
        start2 = start[0:2] + start[3:5] + start[6:]
        end2 = end[0:2] + end[3:5] + end[6:]
        eventname = self.request.get('eventname')
        eventloc = self.request.get('eventloc')
        description = self.request.get('descr')
        #Get event ID & update counter
        qryCounter = Counter.query(Counter.created == True).get()
        eventID = qryCounter.count
        qryCounter.count += 1
        qryCounter.put()
        #Add event ID to invited users lists
        qrySelf = User.query(User.email == user.email()).get()
        qrySelf.eventAcceptedList.append(eventID)
        qrySelf.put()
        emailinvite = self.request.get('hiddeninvite')
        emailinvited = emailinvite.split(", ")
        for email in emailinvited:
            qryFriend = User.query(User.email == email).get()
            qryFriend.eventList.append(eventID)
            qryFriend.put()
        #Create event
        event = Event(eventID = eventID, invitedUsers = emailinvited, acceptedUsers = [user.email()], 
                      name = eventname, location = eventloc, description = description,
                      dateRange = [int(start2), int(end2)])
        event.put()
               
        template = jinja_environment.get_template('processevent.html')
        self.response.out.write(template.render({"eventname": eventname, "eventloc": eventloc , "invited": invite , "startdate": start , "enddate": end , "description": description}))
        self.response.write(BACKHOME)

def listifyEvent(e, abbr):
    date = e.datetime
    if date == None:
        date = "undecided"
    eventlst = [e.eventID, date, json.dumps(e.name), json.dumps(e.location), json.dumps(e.description), e.dateRange]
    if (abbr == 1):
        invited = []
        accepted = []
        rejected = []
        for i in e.invitedUsers:
            qryUser = User.query(User.email == i).get().name
            invited.append(json.dumps(qryUser))
        for i in e.acceptedUsers:
            qryUser = User.query(User.email == i).get().name
            accepted.append(json.dumps(qryUser))
        for i in e.rejectedUsers:
            qryUser = User.query(User.email == i).get().name
            rejected.append(json.dumps(qryUser))
        eventlst.append(invited)
        eventlst.append(accepted)
        eventlst.append(rejected)
    return eventlst
    
class CheckEvent(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        eveLst = qrySelf.eventList
        aeveLst = qrySelf.eventAcceptedList
        eventList = []
        acceptedList = []
        for i in eveLst:
            event = Event.query(Event.eventID == i).get()
            eventList.append(listifyEvent(event, 0))
        for i in aeveLst:
            event = Event.query(Event.eventID == i).get()
            acceptedList.append(listifyEvent(event, 0))
        if len(eventList) == 0:
            eventList = 0
        if len(acceptedList) == 0:
            acceptedList = 0
        template = jinja_environment.get_template('checkevents.html')
        self.response.out.write(template.render({"eLst": eventList, "aeLst": acceptedList}))
        self.response.write(BACKHOME)

class EventDetails(webapp2.RequestHandler):
    def get(self):        
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        id = int(self.request.get('id'))
        qryEvent = Event.query(Event.eventID == id).get()
        event = listifyEvent(qryEvent, 1)
        #check if user can see this event + user status: 0 - invited 1 - accepted 2 - rejected
        status = 0
        if user.email() not in qryEvent.invitedUsers:
            status = 1
            if user.email() not in qryEvent.acceptedUsers:
                status = 2
                if user.email() not in qryEvent.rejectedUsers:
                    self.redirect('/nopermission')
        template = jinja_environment.get_template('eventdetails.html')
        self.response.out.write(template.render({'e': event, 'status': status}))
        
        
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
    ('/updatetime', UpdateTime),
    ('/createevents', CreateEvents),
    ('/processevent', ProcessEvent),
    ('/checkevents', CheckEvent),
    ('/eventdetails', EventDetails),
], debug=True)
