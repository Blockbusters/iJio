var main = function(){
    var input = document.getElementById('venue');
    google.maps.event.trigger( input, 'focus');
    google.maps.event.trigger( input, 'keydown', {keyCode:13});
   
};

var TIMEDELAY = 0.5; // In seconds, set how long to delay before pressing enter for searchbox
setTimeout(main, TIMEDELAY * 1000);

