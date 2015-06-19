var main = function(){
    // Display or hide Friend List Button
    $('#friendbtn').on('click', function(){
        if ($('#friendmenu').css('visibility') == 'visible'){
            $('#friendmenu').css('visibility','hidden');
            $('.friendmenu').find('img').css('visibility','hidden');
        }
        else{
            $('#friendmenu').css('visibility','visible');
            $('.added').find('img').css('visibility','visible');
        }
    });
    // Toggle Add/Remove Friend
    $('.friend').on('click', function(){
        var temp = $(this).find('img');
        var name = $(this).text();
        var textbox = $('#invite');
        // Remove Friend
        if (temp.css('visibility')=='visible'){
            temp.css('visibility','hidden');
            $(this).removeClass('added'); 
            var newbox = "";
            $('.added').each(function(index){
               newbox = newbox + "," + $(this).text(); 
            });
            if (newbox.charAt(0) == ','){
                newbox = newbox.substring(1);
            }
            textbox.val(newbox);
            if (textbox.val() == ""){
                textbox.val("No friends");
            }
        }
        // Add Friend
        else{
            temp.css('visibility','visible');
            $(this).addClass('added');          
            if (textbox.val() == "No friends"){
                textbox.val(name);
            }
            else{
                textbox.val(textbox.val() + "," + name);
            }
        }
    }); 
    // Date picker Start Date
    $('input.datepicker-start').Zebra_DatePicker({
        direction: true, // Only can select dates today or in the future.
        pair: $('input.datepicker-end'), // Paired with another date to create a range
        format: 'd/m/Y', // Format to display date. e.g. 20/06/2015
        onChange: function(d1,d2,d3){ // Clears the end date field whenever start date is changed
            $('.datepicker-end').val("");
        }
    });
    // Date picker End Date
    $('input.datepicker-end').Zebra_DatePicker({
        format: 'd/m/Y', // Format to display date. e.g. 20/06/2015
        direction: [1, 21] // Calendar starts tomorrow and ends 21 days after that.
    });
};

$(document).ready(main);
