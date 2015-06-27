var main = function(){
    // Disabled button upon accepting friend
    $('.accFriend').on('click', function(){
        $(this).attr('disabled', 'disabled');
    });
};

$(document).ready(main);
