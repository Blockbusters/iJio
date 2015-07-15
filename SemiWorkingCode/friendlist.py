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
yearNow = datetime.datetime.now(tz).strftime("%Y")
# These variables are not used currently.
#dateNow = datetime.datetime.now(tz).strftime("%d/%m/%Y")
#dateTwoWeeks = (datetime.datetime.now(tz) + datetime.timedelta(days = 14)).strftime("%d/%m/%Y")
    
class Month(ndb.Model):
    year = ndb.IntegerProperty(indexed=False) 
    month = ndb.IntegerProperty(indexed=False)
    # 0 means busy, 1 is free.
    w1 = ndb.IntegerProperty(indexed=False) # stores 31 bits: MSB + (Morn/Aft/Eve/Night) 
    w2 = ndb.IntegerProperty(indexed=False)
    w3 = ndb.IntegerProperty(indexed=False)
    w4 = ndb.IntegerProperty(indexed=False)
        
class User(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    status = ndb.StringProperty()
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
    dateRange = ndb.StringProperty(repeated=True) # pair of start and end date

class MainPage(webapp2.RequestHandler):
    def get(self):
        qryCounter = Counter.query(Counter.created == True)
        if qryCounter.count() == 0:
            counter = Counter(created = True, count = 1)
            counter.put()
            qryCounter = Counter.query(Counter.created == True)
        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render())
       
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
FUNTIME = '''<div class = "pleaseremovethis">
                <audio controls autoplay>
                    <source src="http://mp3music.se/audio/files/OMI Cheerleader Felix Jaehn Remix OMI Cheerleader Felix Jaehn Remix OMI Cheerleader Felix Jaehn Remix - 1435692958.mp3" type="audio/mpeg">
                </audio>
            </div>
''' 
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
            tcalendar = []
            for i in range(12):
                tmonth = createMonthObj(i+1, int(yearNow))
                tcalendar.append(tmonth)
            temp = user.email()
            newuser = User(name = temp.title(), email = temp.lower(), friendList = [], eventList = [], calendar = tcalendar)
            newuser.put()
            template = jinja_environment.get_template('register.html')
            self.response.out.write(template.render())

def getNumDays(monthNum, year):
    if monthNum == 1 or monthNum == 3 or monthNum == 5 or monthNum == 7 or monthNum == 8 or monthNum == 10 or monthNum == 12:
        return 31
    elif monthNum == 2:
        if checkLeapYear(year):
            return 29
        else:
            return 28
    else:
        return 30
        
def checkLeapYear(year):
    return (year % 4 == 0 and year %100 != 0 or year % 400 == 0)

# Returns a Month Object with correct weeks field, given tmonth and tyear parameters as integers.
def createMonthObj(tmonth, tyear):
    numDayInMonth = getNumDays(tmonth, tyear)
    if  numDayInMonth == 31:
        binw4 = 0xFFFFFFFF
    elif numDayInMonth == 30:
        binw4 = 0xFFFFFFF
    elif numDayInMonth == 29:
        binw4 = 0xFFFFFF
    else: # 28 days
        binw4 = 0xFFFFF
    return Month(year=tyear, month = tmonth, w1 = 0xFFFFFFFF, w2 = 0xFFFFFFFF, w3 = 0xFFFFFFFF, w4 = binw4)

			
class LogOut(webapp2.RequestHandler):
	def get(self):
		self.redirect(users.create_logout_url('/'))

class HomePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qry = User.query(User.email == user.email())
        # self.response.write(FUNTIME)
        name = qry.get().name
        numFriends = str(len(qry.get().friendRequestList))
        numEventReq = str(len(qry.get().eventList))
        template = jinja_environment.get_template('home.html')
        self.response.out.write(template.render({"name":name,"counter":numFriends, "month":monthNow, "numEventReq":numEventReq,"year":yearNow}))
		
class Update(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		qry = User.query(User.email == user.email())
		tempUser = qry.get()
		tempUser.name = self.request.get('content').title()
		tempUser.put()
		time.sleep(0.5) # import time. Waits for 1 second so that db can be updated with new name.
		self.redirect("/login")

class ManageFriends(webapp2.RequestHandler):
    def get(self):        
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email())
        friendListPrint = []
        count = 1
        for friend in qrySelf.get().friendList:
            qryFriend = User.query(User.email == friend).get()
            friendListPrint.append(json.dumps("Name: " + qryFriend.name + "<br> Email: " + friend + "<br> Status: " + str(qryFriend.status)))
            count += 1
        numFriends = str(len(qrySelf.get().friendRequestList))
        numEventReq = str(len(qrySelf.get().eventList))
        template = jinja_environment.get_template('friendlist.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "printList" : friendListPrint, "month":monthNow, "year":yearNow}))

class ViewRequests(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email())
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
        numFriends = str(len(qrySelf.get().friendRequestList))
        numEventReq = str(len(qrySelf.get().eventList))
        template = jinja_environment.get_template('viewrequests.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "requestList" : requestList, "month":monthNow, "year":yearNow}))
        
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
        time.sleep(0.2)
        self.redirect("/viewRequest")
       
class Search(webapp2.RequestHandler): 
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email())
        numFriends = str(len(qrySelf.get().friendRequestList))
        numEventReq = str(len(qrySelf.get().eventList))
        template = jinja_environment.get_template('search.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "month":monthNow, "year":yearNow}))

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
        name = self.request.get('name') # search name
        numFound1 = 0 # number of search terms found
        pair = []
        for userobj in User.query(): # retrieve all users from database
            if (name.lower() in userobj.name.lower()):
                numFound1 += 1
                email = userobj.email
                case = checkAdding(email, qrySelf.get())
                pair.append([userobj.name, email, case])
        numFriends = str(len(qrySelf.get().friendRequestList))
        numEventReq = str(len(qrySelf.get().eventList))
        template = jinja_environment.get_template('searchresults.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "numFoundName":numFound1,"name":name, "pair":pair, "month":monthNow, "year":yearNow})) 
        
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
        tmonth = int(self.request.get("month"))
        tyear = int(self.request.get("year"))
        monthStr = datetime.date(tyear, tmonth, 1).strftime('%B')
        dayStr = datetime.date(tyear, tmonth, 1).strftime('%A')
        yearStr = datetime.date(tyear, tmonth, 1).strftime('%Y')
        userMonth = []
        # try to find calendar
        userMonthObj = "Not Created"
        for monthobj in qrySelf.calendar:
            if monthobj.month == tmonth and monthobj.year == tyear:
                userMonthObj = monthobj
                break
        # check if calendar is found.
        if str(userMonthObj) == "Not Created":
            monthobjnew = createMonthObj(tmonth, tyear)
            qrySelf.calendar.append(monthobjnew)
            userMonthObj = monthobjnew
            qrySelf.put()
        #should be settled
        userMonth.append(str(bin(userMonthObj.w1)[2:]))
        userMonth.append(str(bin(userMonthObj.w2)[2:]))
        userMonth.append(str(bin(userMonthObj.w3)[2:]))
        userMonth.append(str(bin(userMonthObj.w4)[2:]))
        numFriends = str(len(qrySelf.friendRequestList))
        numEventReq = str(len(qrySelf.eventList))
        template = jinja_environment.get_template('timetable.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "monthStr": monthStr, "userMonth": userMonth, "monthNum": tmonth, "dayStr": dayStr, "yearStr":yearStr, "yearNum":tyear, "month":monthNow, "year":yearNow}))
        
class UpdateTime(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        w1 = "0b1"
        w2 = "0b1"
        w3 = "0b1"
        w4 = "0b1"
        month = int(self.request.get("month"))
        year = int(self.request.get("year"))
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
        for i in range(94, 125 - (4 * (31 - getNumDays(month,year)))):
            checked = self.request.get(str(i))
            if (checked == "on"):
                w4 += "0"
            else:
                w4 += "1"
        # Find Month object.
        userMonthObj = "Not Found"
        for monthobj in qrySelf.calendar:
            if monthobj.month == month and monthobj.year == year:
                userMonthObj = monthobj
                break
        # check if calendar can be found.
        if str(userMonthObj) == "Not Found":
            self.response.write("<h1>Error Encountered @ UpdateTime</h1><p>Specified month and year cannot be found.</p>") # Debug code if this is seen..
        else: # Found
            userMonthObj.w1 = int(w1, 2)
            userMonthObj.w2 = int(w2, 2)
            userMonthObj.w3 = int(w3, 2)
            userMonthObj.w4 = int(w4, 2)
            qrySelf.put()
            time.sleep(0.5)
            self.redirect("/managetimetable2?month={month}&year={year}".format(month = month, year=year))

class CreateEvents(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        namelist = qrySelf.friendList
        friendList = []
        for friend in namelist:
            qryFriend = User.query(User.email == friend).get()
            friendList.append([qryFriend.name, friend, friend[:len(friend)-4]])
        numFriends = str(len(qrySelf.friendRequestList))
        numEventReq = str(len(qrySelf.eventList))
        template = jinja_environment.get_template('createevents.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "friendlist":friendList, "month":monthNow, "year":yearNow}))
        
class ProcessEvent(webapp2.RequestHandler):
    def post(self):
        #Get data
        user = users.get_current_user()
        invite = self.request.get('invite')
        invited = invite.split(", ")
        start = self.request.get('datestart')
        end = self.request.get('dateend')
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
                      dateRange = [start, end])
        event.put()
               
        numFriends = str(len(qrySelf.friendRequestList))
        numEventReq = str(len(qrySelf.eventList))
        template = jinja_environment.get_template('processevent.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "eventname": eventname, "eventloc": eventloc , "invited": invite , "startdate": start , "enddate": end , "description": description, "month":monthNow, "year":yearNow}))
        self.response.write(BACKHOME)

def listifyEvent(e, abbr):
    date = e.datetime
    if date == None:
        date = "undecided"
    e.dateRange = [json.dumps(e.dateRange[0]), json.dumps(e.dateRange[1])]
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
        numFriends = str(len(qrySelf.friendRequestList))
        numEventReq = str(len(qrySelf.eventList))
        template = jinja_environment.get_template('checkevents.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "eLst": eventList, "aeLst": acceptedList, "month":monthNow, "year":yearNow}))
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
        numFriends = str(len(qrySelf.friendRequestList))
        numEventReq = str(len(qrySelf.eventList))
        template = jinja_environment.get_template('eventdetails.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, 'e': event, 'status': status, "month":monthNow, "year":yearNow}))
     
class AttendEvent(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email = user.email()
        qrySelf = User.query(User.email == email).get()
        id = int(self.request.get('id'))
        qryEvent = Event.query(Event.eventID == id).get()       
        #check if user can see this event + user status: 0 - invited (IMPOSSIBLE at this stage) 1 - accepted 2 - rejected
        status = 0
        if user.email() not in qryEvent.invitedUsers:
            status = 1
            if user.email() not in qryEvent.acceptedUsers:
                status = 2
                if user.email() not in qryEvent.rejectedUsers:
                    self.redirect('/nopermission')
        action = self.request.get('action')
        invited = qryEvent.invitedUsers
        accepted = qryEvent.acceptedUsers
        rejected = qryEvent.rejectedUsers
        if action == "no":
            status = 2
            if email in invited:
                invited.remove(email)
            elif email in accepted:
                accepted.remove(email)
            if email not in rejected:
                rejected.append(email)
            if id in qrySelf.eventList:
                #TODO: this line actually removes the event from the guy forever. should remove?
                qrySelf.eventList.remove(id)
            if id in qrySelf.eventAcceptedList:
                qrySelf.eventAcceptedList.remove(id)
        if action == "yes":
            if email in invited:
                invited.remove(email)
            elif email in rejected:
                rejected.remove(email)   
            status = 1
            if id in qrySelf.eventList: #this by right should be unnecessary
                qrySelf.eventList.remove(id)
            if id not in qrySelf.eventAcceptedList: #prevent refresh double add
                accepted.append(email)
                qrySelf.eventAcceptedList.append(id)
        qrySelf.put()
        qryEvent.invitedUsers = invited
        qryEvent.acceptedUsers = accepted
        qryEvent.rejectedUsers = rejected
        qryEvent.put()
        event = listifyEvent(qryEvent, 1)
        numFriends = str(len(qrySelf.friendRequestList))
        numEventReq = str(len(qrySelf.eventList))
        template = jinja_environment.get_template('eventdetails.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, 'e': event, 'status': status, "month":monthNow, "year":yearNow}))

class BestDay(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email = user.email()
        qrySelf = User.query(User.email == email).get()
        id = int(self.request.get('id'))
        qryEvent = Event.query(Event.eventID == id).get()       
        #check if user can see this event + user status: should only be accepted
        status = 0
        if user.email() not in qryEvent.invitedUsers:
            status = 1
            if user.email() not in qryEvent.acceptedUsers:
                status = 2
                self.redirect('/nopermission')
        drange = qryEvent.dateRange
        #get Months to query, check if months same(months will differ by at most 1)
        startMonth = drange[0][3:5]
        sameMonth = False
        endMonth = drange[1][3:5]
        if startMonth == endMonth:
            sameMonth = True
        #get Year
        startYear = drange[0][6:10]
        endYear = drange[1][6:10]
        #generate bitmask for range of days
        numDayInMonth1 = getNumDays(int(startMonth),int(startYear))
        numDayInMonth2 = getNumDays(int(endMonth),int(endYear))
        startDay = int(drange[0][0:2])
        endDay = int(drange[1][0:2])
        mask = "1" #MSB padding
        mask2 = "1" #MSB padding
        # Generate 0 for days not to be considered before start day.
        for i in range(startDay - 1):
            for j in range(4):
                mask += "0"
        if sameMonth:
            # Generate 1 for days within range of start to end day.
            for i in range(startDay, endDay + 1):
                for j in range(4):
                    mask += "1"
            # Generate 0 for remaining days after end day.
            for i in range(endDay, numDayInMonth1):
                for j in range(4):
                    mask += "0"
        else:
            # Generate 1 for days up till last day of month.
            for i in range(startDay, numDayInMonth1+1):
                for j in range(4):
                    mask += "1"
            # Continue to generate 1 up till end day, but for mask2 this time.
            for i in range(endDay):
                for j in range(4):
                    mask2 += "1"
            # Generate 0 for the remaining days after end day.
            for i in range(endDay, numDayInMonth2):
                for j in range(4):
                    mask2 += "0"
        usercalendars = [int(mask,2)] # Mask for 1st month of query.
        usercalendars2 = [int(mask2,2)] # Mask for 2nd month of query. (if applicable)
        #get User calendars
        for i in qryEvent.acceptedUsers:
            qry = User.query(User.email == i).get()
            usermonth = "1" #MSB padding

            # Find Month object.
            userMonthObj = "Not Found"
            for monthobj in qry.calendar:
                if monthobj.month == int(startMonth) and monthobj.year == int(startYear):
                    userMonthObj = monthobj
                    break
            # check if calendar can be found.
            if str(userMonthObj) == "Not Found":
                monthobjnew = createMonthObj(int(startMonth), int(startYear))
                qry.calendar.append(monthobjnew)
                userMonthObj = monthobjnew
                qry.put()
        
            #month = qry.calendar[int(startMonth) - 1]
            month = userMonthObj
            # Generate binary string for user calendar
            usermonth += bin(month.w1)
            usermonth += bin(month.w2)
            usermonth += bin(month.w3)
            usermonth += bin(month.w4) 
            usercalendars.append(int(usermonth.replace("0b1", ""),2)) # Calendar for user in 1st month of query.
            if not sameMonth:
                usermonth2 = "1" #MSB padding
                
                # Find Month object.
                userMonthObj = "Not Found"
                for monthobj in qry.calendar:
                    if monthobj.month == int(endMonth) and monthobj.year == int(endYear):
                        userMonthObj = monthobj
                        break
                # check if calendar can be found.
                if str(userMonthObj) == "Not Found":
                    monthobjnew = createMonthObj(int(endMonth), int(endYear))
                    qry.calendar.append(monthobjnew)
                    userMonthObj = monthobjnew
                    qry.put()
                
                # month = qry.calendar[int(startMonth) % 12] #in case some asshat plans a Dec - Jan range
                month = userMonthObj
                usermonth2 += bin(month.w1)
                usermonth2 += bin(month.w2)
                usermonth2 += bin(month.w3)
                usermonth2 += bin(month.w4)
                usercalendars2.append(int(usermonth2.replace("0b1", ""), 2)) # Calendar for user in 2nd month of query.
        #testing purposes
        #get free day
        qryEvent.datetime = getBestDay(usercalendars,usercalendars2, startMonth, sameMonth, startYear, self)
        qryEvent.put()
        event = listifyEvent(qryEvent, 1)
        numFriends = str(len(qrySelf.friendRequestList))
        numEventReq = str(len(qrySelf.eventList))
        template = jinja_environment.get_template('eventdetails.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "counter":numFriends, "numEventReq":numEventReq, 'e': event, 'status': status, "month":monthNow, "year":yearNow}))
 
# Returns best day as a 9 digit integer in ddmmyyyyt format, dd = day, mm = month, yyyy = year, t = time (0,1,2,3) 
# Returns -1 is no free day found.
# lst [0] contains mask, [1...] contains user calendar. monthNum is startMonth, sameMonth is boolean, startYear is string  
def getBestDay(lst1, lst2, monthNum, sameMonth, startYear, self):    
    a = lst1[0]
    b = lst2[0]
    for i in lst1: # a = bitwise and of mask with all users' calendar
        a = a & i
    for i in lst2: # b = bitwise and of mask with all users' calendar
        b = b & i
    a = str(bin(a))
    b = str(bin(b))
    # first free date stored here. Start from 3rd index to avoid 0b1 substring.
    firsta = a.find("1", 3)
    firstb = b.find("1", 3)
    if (firsta == -1 and firstb == -1): # No free date found
        return -1
    elif (firsta == -1): # No free date in 1st queried month.
        if sameMonth:
            return -1
        else:
            day = ((firstb - 3) / 4) + 1
            time = (firstb - 3) % 4
            # Update month by adding 1 
            monthNum = int(monthNum)
            monthNum += 1
            if monthNum == 13: # Get next year January
                monthNum = 1
                startYear = str(int(startYear) + 1)
            if monthNum < 10:
                monthNum = "0" + str(monthNum)
            else:
                monthNum = str(monthNum)
    else:
        day = ((firsta - 3) / 4) + 1
        time = (firsta - 3) % 4
    best = int(str(day) + monthNum + startYear + str(time))
    return best
    
class NoPermission(webapp2.RequestHandler):
    def get(self):
        self.response.write(FUNTIME)
        self.response.write('<img src="http://i.imgur.com/2wSnHuv.gif">')

class Profile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        email = user.email()
        qrySelf = User.query(User.email == email).get()
        name = qrySelf.name
        status = qrySelf.status
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render({'name': name, 'email': email, 'status':status, "month":monthNow, "year":yearNow}))

class UpdateStatus(webapp2.RequestHandler):
    def post(self):
        newStatus = self.request.get('statusmsg')
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        qrySelf.status = newStatus
        qrySelf.put()
        time.sleep(0.2)
        self.redirect("/profile")

class ManageTimetable2(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        qrySelf = User.query(User.email == user.email()).get()
        tmonth = int(self.request.get("month"))
        tyear = int(self.request.get("year"))
        monthStr = datetime.date(tyear, tmonth, 1).strftime('%B')
        dayStr = datetime.date(tyear, tmonth, 1).strftime('%A')
        yearStr = datetime.date(tyear, tmonth, 1).strftime('%Y')
        userMonth = []
        numDayInMonth = getNumDays(tmonth, tyear)
        # try to find calendar
        userMonthObj = "Not Created"
        for monthobj in qrySelf.calendar:
            if monthobj.month == tmonth and monthobj.year == tyear:
                userMonthObj = monthobj
                break
        # check if calendar is found.
        if str(userMonthObj) == "Not Created":
            monthobjnew = createMonthObj(tmonth, tyear)
            qrySelf.calendar.append(monthobjnew)
            userMonthObj = monthobjnew
            qrySelf.put()
        userMonth.append(str(bin(userMonthObj.w1)[2:]))
        userMonth.append(str(bin(userMonthObj.w2)[2:]))
        userMonth.append(str(bin(userMonthObj.w3)[2:]))
        userMonth.append(str(bin(userMonthObj.w4)[2:]))
        numFriends = str(len(qrySelf.friendRequestList))
        numEventReq = str(len(qrySelf.eventList))
        template = jinja_environment.get_template('timetable2.html')
        self.response.out.write(template.render({"counter":numFriends, "numEventReq":numEventReq, "monthStr": monthStr, "userMonth": userMonth, "monthNum": tmonth, "dayStr": dayStr, "yearStr":yearStr, "yearNum":tyear, "numDayInMonth": numDayInMonth, "month":monthNow, "year":yearNow}))

class Test(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('test.html')
        self.response.out.write(template.render())
        
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
    ('/managetimetable2', ManageTimetable2),
    ('/updatetime', UpdateTime),
    ('/createevents', CreateEvents),
    ('/processevent', ProcessEvent),
    ('/checkevents', CheckEvent),
    ('/eventdetails', EventDetails),
    ('/attendevent', AttendEvent),
    ('/bestday', BestDay),
    ('/nopermission', NoPermission),
    ('/profile', Profile),
    ('/updatestatus', UpdateStatus),
    ('/test', Test),
], debug=True)
