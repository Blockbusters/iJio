var main = function(){ 
    $('.arrow-next').click(function(){
          var currentSlide = $('.active-slide');
          var nextSlide = currentSlide.next();
          var currentDot = $('.active-dot');
          var nextDot = currentDot.next();
          if (nextSlide.length === 0){
            nextSlide = $('.slide').first();
            nextDot = $('.dot').first();
          }
          currentSlide.fadeOut(fadeTime).removeClass('active-slide');
          nextSlide.fadeIn(fadeTime).addClass('active-slide');
          
          currentDot.removeClass('active-dot');
          nextDot.addClass('active-dot');
		  
		  clearInterval(interval);
		  interval = setInterval(autoClickNext, autoClickTime);
    });
    
    $('.arrow-prev').click(function(){
        var currentSlide = $('.active-slide');
        var prevSlide = currentSlide.prev();
        var currentDot = $('.active-dot');
        var prevDot = currentDot.prev();
        if (prevSlide.length === 0){
            prevSlide = $('.slide').last();
            prevDot = $('.dot').last();
        }
        currentSlide.fadeOut(fadeTime).removeClass('active-slide');
        prevSlide.fadeIn(fadeTime).addClass('active-slide');
        currentDot.removeClass('active-dot');
        prevDot.addClass('active-dot');
		
		clearInterval(interval);
		interval = setInterval(autoClickNext, autoClickTime);
    });
};

/* Auto click next arrow*/
var autoClickNext = function(){
	document.getElementById('autoClick').click();
};

// Constant values
var autoClickTime = 5000; // in milliseconds. Time interval to click next image.
var fadeTime = 600;       // in milliseconds. Time interval to fade image on click next/prev image.
//-----------------------------------------------------------------------------------------------------------
$(document).ready(main); // Runs main method once document (html) is fully loaded.
var interval = setInterval(autoClickNext, autoClickTime); // Runs the auto-clicker method periodically.

