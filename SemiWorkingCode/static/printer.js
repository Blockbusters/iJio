function printTimetable(lstBin) {
    counter = 1;
    for (i = 0; i < 4; i++) {
        str = lstBin[i];
        len = str.length;
        for (var j = 1; j < len; j++) {
            if ((counter - 1) % 4 == 0) {
            //Find way to print day of week
                document.write("<br> Day ");
                document.write(((counter - 1) / 4) + 1);
            }
            if (str[j] == 0) {
                document.write("<input type='checkbox' checked = 'checked' name = ");
                document.write(counter);
                document.write("></input>");
            } else {
                document.write("<input type='checkbox' name = ");
                document.write(counter);
                document.write("></input>");
            }
            counter++;
        }
    }
}

function printEvents(lstlstEvent) {
    if (lstlstEvent == 0) {
        document.write('No events at the moment. <a class = "link" href = "/createevents">Why not create one?</a>');
    } else {
        for (var i = 0; i < lstlstEvent.length; i++) {
            var event = lstlstEvent[i]
            document.write('<div class = "event">');
            printEvent(event);
            document.write('</div>');
            
            }
    }
}
//      0       1     2       3          4           5         6        7          8
//  [eventID, date, name, location, description, dateRange, invited, accepted, rejected]
function printEvent(lstEvent) {
    document.write(lstEvent[2] + " at " + lstEvent[3] +" on " + stringifyTime(lstEvent[1]))
    document.write('  <a class = "link" href = /eventdetails?id=');
    document.write(lstEvent[0])
    document.write('><sub> View Details</sub></a>');
}

function stringifyTime(num) {
    if (num == "undecided") {
        return "undecided";
    }
    if (num == -1){
        return "Not possible";
    }
    time = num % 10
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
    if (num < 10000){
        toPadZero = true;
    }
    num = num.toString();
    if (toPadZero){
        num = "0" + num
    }
    return num.substring(0, 2) + "/" + num.substring(2, 4) + ", " + t;
}
function printE(lstEvent, status) {
    document.write('<div class="row"><div class="col-md-6">');
    document.write('Location: </div><div class="col-md-6">');
    document.write(lstEvent[3]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-6">');
    document.write('Date Range: </div><div class="col-md-6">');
    var start = lstEvent[5][0].replace('\\"',"");
    var end = lstEvent[5][1].replace('\\"',"");
    document.write(start + " to " + end);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-6">');
    document.write('Description: </div><div class="col-md-6">');
    document.write(lstEvent[4]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-6">');
    document.write('Attending: </div><div class="col-md-6">');
    document.write(lstEvent[7]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-6">');
    document.write('Invited: </div><div class="col-md-6">');
    document.write(lstEvent[6]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-6">');
    document.write('Date: </div><div class="col-md-6">');
    document.write(stringifyTime(lstEvent[1]));
    document.write(' <button class="calcdate" id = "best" onClick = \'location.href="/bestday?id=');
    document.write(lstEvent[0]);
    if (lstEvent[1] == "undecided") {
        document.write('"\'>Get best date</button>');
        
    } else {
        document.write('"\'>Recalculate</button>');
    }
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-3"></div>');
    document.write('<div class="col-md-3"><button id = "attend" onClick = \'location.href="/attendevent?action=yes&id=');
    document.write(lstEvent[0]);
    document.write('"\'>Attend</button></div>');
    document.write('<div class="col-md-3"><button id = "reject" onClick = \'location.href="/attendevent?action=no&id=');
    document.write(lstEvent[0]);
    document.write('"\'>Reject</button></div>');
    document.write('</div>');
    
    //disable buttons based on status: 0 - invited 1 - accepted 2 - rejected
    if (status == 1) {
        var button = document.getElementById("attend")
        button.className += "disabled";
        button.disabled = true;
    }
    if (status == 2) {
        var button = document.getElementById("reject")
        button.className += "disabled";
        button.disabled = true;
        var link = document.getElementById("best")
        link.href= "#";
    }
    
}
