var main = function(){
    // Toggle Add/Remove Friend
    $('.accFriend').on('click', function(){
        $(this).attr('disabled', 'disabled');
    });
};

$(document).ready(main);
