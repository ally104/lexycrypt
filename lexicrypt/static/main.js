$(function() {
    $('#login').click(function() {
        navigator.id.getVerifiedEmail(function(assertion) {
            if(assertion) {
                $('form input').val(assertion);
                $('form').submit();
            }
        });
    });

    $('a.delete').click(function(ev) {
        ev.preventDefault();
    });

    $('.decrypt button').click(function() {
        var self = $(this);
        var message = self.parent().find('.message');
        $('.decrypt .message').hide();
        $.ajax({
            url: '/get_message',
            data: { "message": self.parent().parent().find('img').attr('src') },
            type: 'POST',
            dataType: 'json',
            success: function(data) {
               message.html(data['message']);
               message.show();
            }
        });
    });

    $('body').click(function() {
       $('.decrypt .message').hide(); 
    });
});