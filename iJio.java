import java.util.*;
import java.util.Map.*;

public class IJio {
	private ArrayList<User> users;
	
	// Constants
	public static final int TODAY_DAY = 13;
	public static final int TODAY_MONTH = 5;
	public static final int TODAY_YEAR = 2015;
	public static final String TODAY_TIME = "AM";
	public static final int TIMESLOTS = 21; // Number of time slots to check for available date.
	// End constants
	public static void main (String[] args){
		Scanner sc = new Scanner (System.in);
		IJio app = new IJio();
		app.run(sc);
	}
	
	public IJio(){
		users = new ArrayList<User>();
	}
	
	// Adds user to application:
	// Format: add <name>
	// Pre-cond: new User added must be unique/doesn't already exist in users array list.
	private void addUser(Scanner sc){
		String name = sc.next();
		
		User newUser = new User(name);
		if (users.contains(newUser)){
			System.out.println(name + " already exists in the application!");
		}
		else{
			users.add(newUser);
			System.out.println(name + " has been added to the application.");
		}
	}
	
	// Makes both given names friends of each other.
	// Format: friend <name> <name>
	// Pre-cond: both names already exist in users array list.
	private void addFriends(Scanner sc){
		String name1 = sc.next();
		String name2 = sc.next();
		User friend1 = getUser(name1);
		User friend2 = getUser(name2);
		if (friend1 != null && friend2 != null){
			friend1.addFriend(name2);
			friend2.addFriend(name1);
			System.out.println(name1 + " and " + name2 + " have become friends!");
		}
		else{
			System.out.println("[Error] Input user does not exist!");
		}
	}
	
	// Add an activity to User personal calendar.
	// Format: calendar <name> <dd mm yyyy> <am/nn/pm> <activity>
	// pre-cond: user must already exist in users array list.
	private void addCalendar(Scanner sc){
		String name = sc.next();
		User curr = getUser(name);
		if (curr!=null){ // User exist
			Date temp = null;
			String activity = "";
			do{
				try{
					int day = sc.nextInt();
					int month = sc.nextInt();
					int year = sc.nextInt();
					String time = sc.next();
					activity = sc.next();
					temp = new Date(day,month,year,time); // might throw Exception.
					curr.addCalendar(temp, activity);
				}
				catch (IllegalArgumentException e){ // invalid date
					System.out.println(e.getMessage());
				}
				catch (InputMismatchException e){ // invalid scanning
					System.out.println("Please enter in following format dd mm yyyy am/nn/pm");
					sc.nextLine(); // clears the remaining input.
				}
			}while(temp == null);
			System.out.println(name + " will be " + activity + " on " + temp);
		}
		else{ // User does not exist.
			System.out.println("[Error] Input user does not exist!");
		}
	}
	
	// Creates an event to JIO people
	// Format: event <name> <where> <dowhat>
	// pre-cond: user must already exist in users array list.
	private void addEvent(Scanner sc){
		String name = sc.next();
		User curr = getUser(name);
		if (curr!=null){ // user exists.
			boolean found = false;
			String where = sc.next();
			String doWhat = sc.next();
			// Generate friend list.
			ArrayList <String> list = curr.getFriends();
			ArrayList <User> friendList = new ArrayList <User>();
			for (int i=0; i<list.size(); i++){
				friendList.add(new User(getUser(list.get(i))));
			}
			friendList.add(new User(curr));
			// Find Date.
			Date today = new Date(TODAY_DAY, TODAY_MONTH, TODAY_YEAR, TODAY_TIME);
			for (int i=0; i<TIMESLOTS; i++){ // Check next # time slots for outing.
				today = today.nextSlot();
				found = true;
				for (int j=0; j<friendList.size(); j++){
					if (!friendList.get(j).checkFree(today)){
						found = false;
						break;
					}
				}
				if (found){
					break;
				}
			}
			// Determine if any common date is found or not.
			if (found){
				System.out.println("Possible to go " + where + " for " + doWhat + " on "
						+ today);
				Event event = new Event(today, where, doWhat); 
				for (int person=0; person<friendList.size(); person++){
					User affected = getUser(friendList.get(person).getName()) ;
					affected.addEvent(event);
					affected.addCalendar(event.getDate(),doWhat + "@" + where);
				}
			}
			else{
				System.out.println("Not possible for event!");
			}
		}
		else{ // User doesn't exist.
			System.out.println("[Error] Input user does not exist!");
		}
	}
	
	// Views the calendar or event for user.
	// Format: view calendar/events <name>
	// pre-cond: user must already exist in users array list.
	private void view(Scanner sc){
		String type = sc.next();
		if (type.equals("calendar")){ // View Calendar
			String name = sc.next();
			User user = getUser(name);
			if (user!=null){ // user exists.
				viewCalendar(user);
			}
			else{ // user does not exist.
				System.out.println("[Error] Input user does not exist!");
			}
		}
		else if (type.equals("events")){ // View Events
			String name = sc.next();
			User user = getUser(name);
			if (user!=null){ // user exists.
				viewEvents(user);
			}
			else{ // user does not exist.
				System.out.println("[Error] Input user does not exist!");
			}
		}
		else{ // Invalid input.
			sc.nextLine();
			System.out.println("[Error] Invalid command!");
		}
	}
	
	// Views the calendar for given user.
	private void viewCalendar(User user){
		Set<Entry<Date, String>> hashSet = user.getCalendar().entrySet();
		System.out.println("Activities for " + user.getName() + ":");
		for (Entry<Date,String> entry: hashSet){
			System.out.println(entry.getKey() + ": " + entry.getValue());
		}
	}
	
	// Views the events for given user.
	private void viewEvents(User user){
		ArrayList <Event> eventList = user.getEvents();
		Collections.sort(eventList);
		System.out.println("Events for " + user.getName() + ":");
		for (Event eve: eventList){
			System.out.println(eve);
		}
	}
	
	// Runs according to the input command.
	public void run(Scanner sc){
		showCommands();
		
		String type = sc.next();
		while (!type.equals("quit")){ 
			if (type.equals("add")){ // Add a user.
				addUser(sc);
			}
			else if (type.equals("friend")){ // Create friendship link between 2 users.
				addFriends(sc);
			}
			else if (type.equals("calendar")){ // Adds an activity to User personal calendar.
				addCalendar(sc);
			}
			else if (type.equals("event")){ // Creates an event to go out with friends.
				addEvent(sc);
			}
			else if (type.equals("view")){ // Views the calendar for user.
				view(sc);
			}
			else{ // Invalid input.
				System.out.println("[Error] Invalid command!");
				sc.nextLine();
			}
			type = sc.next();
		}
		// Quit application.
	}
	
	private void showCommands(){
		System.out.println("Welcome to IJio!!!");
		System.out.println("List of commands: ");
		System.out.println("1. Add User: add <name>  // e.g. add billy");
		System.out.println("2. Add Friend: friend <name> <name>  // e.g. friend billy ryan");
		System.out.println("3. Add calendar: calendar <name> <dd mm yyyy am/nn/pm> <activity>"
				+ "e.g. calendar billy 1 3 2016 nn dancing");
		System.out.println("4. Add event: event <name> <where to go> <what to do>"
				+ "e.g. event billy equestria dancing");
		System.out.println("5. View calendar: view calendar <name> // e.g. view calendar billy");
		System.out.println("6. View events: view events <name> // e.g. view events billy");
		System.out.println("7. Quit: quit");
	}
		
	
	// Returns User with given name. Returns null if User does not exist.
	public User getUser(String name){
		for (int i=0; i<users.size(); i++){
			if (users.get(i).getName().equals(name)){
				return users.get(i);
			}
		}
		return null; // User does not exist.
	}
}

class User{
	private String name;
	private ArrayList<String> friends;
	private ArrayList<Event> events;
	private HashMap<Date, String> calendar;
	
	// Constructors
	public User(User another){
		name = another.getName();
		friends = another.getFriends();
		calendar = another.getCalendar();
		events = another.getEvents();
	}
	public User(String name){
		this.name = name;
		friends = new ArrayList<String>();
		calendar = new HashMap<Date, String>();
		events = new ArrayList<Event>();
	}
	
	// Check if user is free on the given date. Returns true if user is free, false otherwise.
	public boolean checkFree(Date date){
		return !calendar.containsKey(date);
	}
	
	public ArrayList<String> getFriends(){
		return new ArrayList<String>(friends);
	}
	public HashMap<Date, String> getCalendar(){
		return new HashMap<Date, String>(calendar);
	}
	public ArrayList<Event>getEvents(){
		return new ArrayList<Event>(events);
	}
	
	@Override
	public boolean equals(Object obj){
		if (obj instanceof User){
			User user = (User) obj;
			return getName().equals(user.getName());
		}
		else{
			return false;
		}
	}
	
	public String getName(){
		return name;
	}
	
	// Add event to calendar. 
	public void addCalendar(Date date, String descr){
		calendar.put(date, descr);
	}
	
	// Add friend (as name) to friend list of this user.
	public void addFriend(String friend){
		friends.add(friend);
	}
	
	// Add an event to events array list.
	public void addEvent(Event event){
		events.add(event);
	}
}

class Event implements Comparable<Event>{
	private Date date;
	private String where;
	private String what;
	
	public Event(Date date, String where, String what){
		this.date = date;
		this.where = where;
		this.what = what;
	}
	
	@Override
	public int compareTo(Event other){
		return date.compareTo(other.getDate());
	}
	
	public Date getDate(){
		return date;
	}
	
	@Override
	public String toString(){
		return "[" + date + "] " + what + " at " + where; 
	}
}

class Date implements Comparable<Date>{
	private int year;
	private int month;
	private int day;
	private String time;
	
	// Constructors
	public Date (int day, int month, int year){
		this(day, month, year, "AM");
	}
	public Date(int day, int month, int year, String time) throws IllegalArgumentException{
		time = time.toUpperCase();
		if(checkValidity(day, month, year, time)){
			this.year = year;
			this.month = month;
			this.day = day;
			this.time = time;
		}
		else{
			throw new IllegalArgumentException("Invalid date entered!");
		}
	}
	
	@Override
	public int hashCode(){
		int result = 0;
		
		result = day;
		result = 31*result + month;
		result = 31*result + year;
		result = 31*result + (time  !=null ? time.hashCode() : 0);
	      
	    return result;
	}
	
	// Returns the next time slot/date in the calendar.
	public Date nextSlot(){
		String t = getTime();
		int d = getDay();
		int m = getMonth();
		int y = getYear();
		
		if (t.equals("AM")){
			return new Date(d,m,y,"NN");
		}
		else if (t.equals("NN")){
			return new Date(d,m,y,"PM");
		}
		// Else time is PM
		
		d++;
		if (checkValidity(d,m,y)){
			return new Date(d, m, y);
		}
		
		// Day beyond what's possible for the month.
		d = 1;
		m++;
		if (checkValidity(d,m,y)){
			return new Date(d, m, y);
		}
		
		// Month beyond December
		return new Date(1, 1, y+1);
	}
	
	public int getYear(){
		return year;
	}
	public int getMonth(){
		return month;
	}
	public int getDay(){
		return day;
	}
	public String getTime(){
		return time;
	}
	
	@Override
	public int compareTo(Date other){
		if (year != other.getYear()){
			return (year > other.getYear() ? 1 : -1);
		}
		else if (month != other.getMonth()){
			return (month > other.getMonth() ? 1 : -1);
		}
		else if (day != other.getDay()){
			return (day > other.getDay() ? 1 : -1);
		}
		else if (!time.equals(other.getTime())){
			String otherTime = other.getTime();
			if (time.equals("AM")){
				return -1;
			}
			else if (time.equals("NN")){
				if (otherTime.equals("AM")){
					return 1;
				}
				else{ // otherTime is "PM"
					return -1;
				}
			}
			else{ // time is "PM"
				return 1;
			}
		}
		else{ // Same date.
			return 0;
		}
	}
	
	@Override
	public String toString(){
		String monthField;
		switch(month){
			case 1:
				monthField = "January";
				break;
			case 2:
				monthField = "February";
				break;
			case 3:
				monthField = "March";
				break;
			case 4:
				monthField = "April";
				break;
			case 5:
				monthField = "May";
				break;
			case 6:
				monthField = "June";
				break;
			case 7:
				monthField = "July";
				break;
			case 8:
				monthField = "August";
				break;
			case 9:
				monthField = "September";
				break;
			case 10:
				monthField = "October";
				break;
			case 11:
				monthField = "November";
				break;
			case 12:
				monthField = "December";
				break;
			default:
				monthField = "dummy";
		}
		return day + " " + monthField + " " + year + " " + time;
	}
	
	@Override
	public boolean equals(Object obj){
		if (obj instanceof Date){
			Date temp = (Date) obj;
			return (getDay() == temp.getDay() && getMonth() == temp.getMonth()
					&& getYear() == temp.getYear() && time.equals(temp.getTime()));
					
		}
		else{
			return false;
		}
	}
	
	// Overloaded method
	private static boolean checkValidity(int day, int month, int year){
		return checkValidity(day, month, year, "AM");
	}
	// Checks if given date and time are valid or not.
	// Returns true if date is valid (day-month-year combination exists in calendar, and time is 
	// either AM, NN or PM.) Returns false if date/time is invalid.
	private static boolean checkValidity(int day, int month, int year, String time){
		// Check time
		if (!time.equals("AM") && !time.equals("NN") && !time.equals("PM")){
			return false;
		}
		// Check date
		switch (month){
			case 1: case 3: case 5: case 7: case 8: case 10: case 12: // months with 31 days.
				return (day > 0 && day <=31);	
			case 2: // months with 28 or 29 days, leap-year depending.
				if (isLeapYear(year)){
					return (day > 0 && day <=29);
				}
				else{
					return (day > 0 && day <=28);
				}
			case 4: case 6: case 9: case 11: // months with 30 days
				return (day > 0 && day <=30);
			default:
				return false;
		}
	}
	
	// Returns true if given year is a leap year, false otherwise.
	private static boolean isLeapYear(int year){
		if (year%4!=0){
			return false;
		}
		else if (year%100!=0){
			return true;
		}
		else if(year%400!=0){
			return false;
		}
		else{
			return true;
		}	
	}
}
