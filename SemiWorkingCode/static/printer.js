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
    document.write(lstEvent[2] + " at " + lstEvent[3] +" on " + lstEvent[1])
    document.write('  <a class = "link" href = /eventdetails?id=');
    document.write(lstEvent[0])
    document.write('><sub> View Details</sub></a>');
}

function printE(lstEvent) {
    document.write('<div class="row"><div class="col-md-6">');
    document.write('Location: </div><div class="col-md-6">');
    document.write(lstEvent[3]);
    document.write('</div></div>');
    
    document.write('<div class="row"><div class="col-md-6">');
    document.write('Date: </div><div class="col-md-6">');
    document.write('TODO: date if chosen, data range if not');
    document.write(lstEvent[1]);
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
}
