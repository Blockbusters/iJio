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
