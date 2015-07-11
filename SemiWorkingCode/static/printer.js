//dayStr is the first day of the month
function printTimetable(lstBin,dayStr) {
    counter = 1;
    for (i = 0; i < 4; i++) {
        str = lstBin[i];
        len = str.length;
        for (var j = 1; j < len; j++) {
            if ((counter - 1) % 4 == 0) {
                document.write("<br> Day ");
                document.write(((counter - 1) / 4) + 1);              
            }
            if (str[j] == 0) {
                document.write("&#09;<input type='checkbox' checked = 'checked' name = '");
                document.write(counter);
                document.write("' id = '");
                document.write(counter - 1);
                document.write("'></input>");
            } else {
                document.write("&#09;<input type='checkbox' name = '");
                document.write(counter);
                document.write("' id = '");
                document.write(counter - 1);
                document.write("'></input>");
            }
            if ((counter - 1) % 4 == 3){
                document.write("(" + convertDay(dayStr, counter) + ")");
            }
            counter++;
        }
    }
}

function printTimetable2(dayStr, numDayInMonth, lstBin) {
    document.write('<img src="static/DayNames.png"><p>')
    var Cal = "Cal" + dayStr
    document.write("<img src = 'static/");
    document.write(Cal);
    document.write(".png'>");
    //get first day that has not been printed
    var daysArray = ["Sunday","Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    var lastDay = 29;
    var numOfFirstDay = 0;
    for (; daysArray[numOfFirstDay] != dayStr; numOfFirstDay++){
        lastDay--;
    }
    //print missing days
    document.write("<br>");
    var linebreakcounter = 0;
    for (;lastDay <= numDayInMonth; lastDay++) {
        if (linebreakcounter != 0 && linebreakcounter % 7 == 0) {
            document.write("<br>");
        }
        document.write("<img src = 'static/");
        document.write(lastDay);
        document.write(".png'>");
        linebreakcounter++;
    }
    //print empty squares
    while (linebreakcounter % 7 != 0) {
            document.write("<img src = 'static/blanksq.png'>");
            linebreakcounter++;
    }
    var numlinesprinted = (linebreakcounter / 7) + 4;
    //second layer starts here
    document.write("</span><span class= 'layer2'><br>");
    //concatenate week string, then split into array of adjusted weeks.
    var weekStr = "";
    for (i = 0; i < 4; i++) {
        weekStr += lstBin[i].substring(1);
    }
    var tempnum = (7 - numOfFirstDay) * 4;
    var adjustedWeeks = [weekStr.substring(0, tempnum)];
    for (var i = 1; i < numlinesprinted; i++) {
        if (i != numlinesprinted) {
            adjustedWeeks.push(weekStr.substring(tempnum, tempnum + 28));
            tempnum += 28;
        } //last week
        else{
            adjustedWeeks.push(weekStr.substring(tempnum));
        }
        
    }
    printWeeksinCalendar(adjustedWeeks, numOfFirstDay);
    //shift second layer up
    var toshift = numlinesprinted + "00px"
    $(".layer2").css("bottom", toshift);
}

function printWeeksinCalendar(adjustedWeeks, firstDayNum) {
    //print first week pt. 1
    for (var i = firstDayNum; i > 0; i--) {   
        document.write("<img src = 'static/slashleftsq.png'><img src = 'static/slashrightsq.png'>");
    }
    var week = adjustedWeeks[0]
    for (var i = 0; i < week.length; i += 4) {
        if (week[i] == 0) {
                document.write("<img src='static/redsq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(i);
                document.write("'>");
            } else {
                document.write("<img src='static/greensq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(i);
                document.write("'>");
            }
        if (week[i + 1] == 0) {
                document.write("<img src='static/redsq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(i + 1);
                document.write("'>");
            } else {
                document.write("<img src='static/greensq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(i + 1);
                document.write("'>");
            }
    }
    document.write("<br>");
    //print first week pt. 2
    for (var i = firstDayNum; i > 0; i--) {   
        document.write("<img src = 'static/slashrightsq.png'><img src = 'static/slashleftsq.png'>");
    }
    var week = adjustedWeeks[0]
    for (var i = 2; i < week.length; i += 4) {
        if (week[i] == 0) {
                document.write("<img src='static/redsq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(i);
                document.write("'>");
            } else {
                document.write("<img src='static/greensq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(i);
                document.write("'>");
            }
        if (week[i + 1] == 0) {
                document.write("<img src='static/redsq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(i + 1);
                document.write("'>");
            } else {
                document.write("<img src='static/greensq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(i + 1);
                document.write("'>");
            }
    }
    var k = week.length;
    document.write("<br>");
    //print remaining weeks
    for (var i = 1; i < adjustedWeeks.length; i++) {
        week = adjustedWeeks[i]
        for (var j = 0; j < week.length; j += 4) {
            if (week[j] == 0) {
                document.write("<img src='static/redsq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(j + k);
                document.write("'>");
            } else {
                document.write("<img src='static/greensq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(j + k);
                document.write("'>");
            }
            if (week[j + 1] == 0) {
                document.write("<img src='static/redsq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(j + 1 + k);
                document.write("'>");
            } else {
                document.write("<img src='static/greensq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(j + 1 + k);
                document.write("'>");
            }
        }
        document.write("<br>");
        //round 2
        for (var j = 2; j < week.length; j += 4) {
            if (week[j] == 0) {
                document.write("<img src='static/redsq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(j + k);
                document.write("'>");
            } else {
                document.write("<img src='static/greensq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(j + k);
                document.write("'>");
                }
            if (week[j + 1] == 0) {
                document.write("<img src='static/redsq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(j + 1 + k);
                document.write("'>");
            } else {
                document.write("<img src='static/greensq50.png' onclick='updatesq(id)' id = 'sq");
                document.write(j + 1 + k);
                document.write("'>");
            }
        }
        k += 28;
        document.write("<br>");
    }
    //can insert code for printing over blanks here but should be unnecessary/damn annoying
}

function updatesq(id) {
    var sq = document.getElementById(id);
    var checkboxid = id.substring(2);
    var check = document.getElementById(checkboxid);
    if (check.checked) {
        sq.src = "static/greensq50.png";
        check.checked = false;
    } else {
        sq.src = "static/redsq50.png";
        check.checked = true;
    }
}

function convertDay(dayStr, counter){
    var daysArray = ["Sunday","Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    var index = -1;
    for (var i=0; i<7; i++){
        if (dayStr === daysArray[i]){
            index = i;
            break;
        }
    }
    return daysArray[(index + parseInt((counter-1)/4)) % 7];
}

function printEvents(lstlstEvent) {
    if (lstlstEvent == 0) {
        document.write('No events at the moment. <a class = "link" href = "/createevents">Why not create one?</a>');
    } else {
        for (var i = 0; i < lstlstEvent.length; i++) {
            var event = lstlstEvent[i];
            document.write('<div class = "event">');
            printEvent(event);
            document.write('</div>');
            
            }
    }
}
//      0       1     2       3          4           5         6        7          8
//  [eventID, date, name, location, description, dateRange, invited, accepted, rejected]
function printEvent(lstEvent) {
    document.write(lstEvent[2] + " at " + lstEvent[3] +" on " + stringifyTime(lstEvent[1]));
    document.write('  <a class = "link" href = /eventdetails?id=');
    document.write(lstEvent[0]);
    document.write('><sub> View Details</sub></a>');
}

function stringifyTime(num) {
    if (num == "undecided") {
        return "undecided";
    }
    if (num == -1){
        return "Not possible";
    }
    time = num % 10;
    toPadZero = false;
    if (time == 0) {
        t =  "Morning";
    } else if (time == 1) {
        t = "Afternoon";
    } else if (time == 2) {
        t = "Evening";
    } else {
        t = "Night";
    }
    if (num < 100000000){
        toPadZero = true;
    }
    num = num.toString();
    if (toPadZero){
        num = "0" + num;
    }
    
    var date = new Date(parseInt(num.substring(4,8)), parseInt(num.substring(2,4))-1, parseInt(num.substring(0,2)));
    var day = date.getDay();
    var daysArray = ["Sunday","Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    
    return num.substring(0, 2) + "/" + num.substring(2, 4) + "/" + num.substring(6,8) + "(" + daysArray[day]  + "), " + t;
}
function printE(lstEvent, status) {
    document.write('<div class="row"><div class="col-md-5">');
    document.write('Location: </div><div class="col-md-7">');
    document.write(lstEvent[3]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-5">');
    document.write('Date Range: </div><div class="col-md-7">');
    var start = lstEvent[5][0].replace('\\"',"");
    var end = lstEvent[5][1].replace('\\"',"");
    document.write(start + " to " + end);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-5">');
    document.write('Description: </div><div class="col-md-7">');
    document.write(lstEvent[4]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-5">');
    document.write('Attending: </div><div class="col-md-7">');
    document.write(lstEvent[7]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-5">');
    document.write('Invited: </div><div class="col-md-7">');
    document.write(lstEvent[6]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-5">');
    document.write('Date: </div><div class="col-md-7">');
    document.write(stringifyTime(lstEvent[1]));
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-2"></div>');
    document.write('<div class="col-md-3"><button id = "attend" onClick = \'location.href="/attendevent?action=yes&id=');
    document.write(lstEvent[0]);
    document.write('"\'>Attend</button></div>');
    document.write('<div class="col-md-3"><button id = "reject" onClick = \'location.href="/attendevent?action=no&id=');
    document.write(lstEvent[0]);
    document.write('"\'>Reject</button></div>');
    document.write('<div class="col-md-3">');
    document.write(' <button class="calcdate" id = "best" onClick = \'location.href="/bestday?id=');
    document.write(lstEvent[0]);
    if (lstEvent[1] == "undecided") {
        document.write('"\'>Get best date</button>');        
    } else {
        document.write('"\'>Recalculate</button>');
    }
    document.write('</div></div>');
    
    
    //disable buttons based on status: 0 - invited 1 - accepted 2 - rejected
    if (status == 1) {
        var button = document.getElementById("attend");
        button.className += "disabled";
        button.disabled = true;
    }
    if (status == 2) {
        var button = document.getElementById("reject");
        button.className += "disabled";
        button.disabled = true;
        var link = document.getElementById("best");
        link.href= "#";
    }
    
}
