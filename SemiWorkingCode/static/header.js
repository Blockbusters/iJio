function updateHeader(friendreq, eventreq){
    if (friendreq != "0") {
        var friend = document.getElementById("friend");
        friend.src = "static/friendnew.png";
    }
    if (eventreq != "0") {
        var e = document.getElementById("event");
        e.src = "static/newevent.png";
    }

}
