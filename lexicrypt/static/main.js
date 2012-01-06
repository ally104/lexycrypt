$(function() {
    var email_item_length = 16;

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
        var message = $('#message');
        $('.decrypt .message').hide();
        $.ajax({
            url: '/get_message',
            data: { "message": self.parent().parent().find('img').attr('src') },
            type: 'POST',
            dataType: 'json',
            success: function(data) {
               message.text(data['message']);
               message.show();
            }
        });
    });

    $('body').click(function() {
       $('#message').hide(); 
    });

    $('.accessors a.delete').click(function(ev) {
        ev.preventDefault();
        var self = $(this);
        var bottom = (26 * self.closest('.accessors').find('li.email').length) + self.closest('.accessors').find('li.email').length + 33;
        $.ajax({
            url: '/remove_email',
            data: { "message": self.data('message'), "email": self.data('email') },
            type: 'POST',
            dataType: 'json',
            success: function(data) {    
                self.closest('.accessors').css({'bottom': '-' + bottom + 'px'});
                self.parent().remove();
            }
        });
    });

    $('.accessors li.toggle').click(function() {
        var self = $(this);
        var bottom = 26;
        $('.your-messages > li').removeClass('selected');
        
        if(self.parent().hasClass('hidden')) {
            // calculate how far the bottom should be based on
            // how many emails there are.
            $('.your-messages > li').addClass('hidden');
            self.closest('.your-messages > li').removeClass('hidden');

            bottom = (bottom * self.parent().find('li.email').length) + self.parent().find('li.email').length + bottom + 34;
            self.parent().css({'bottom': '-' + bottom + 'px'});
            self.closest('.your-messages > li').addClass('selected');
            self.parent().removeClass('hidden');
            self.text('Hide');
        } else {
            self.parent().css({'bottom': '-26px'});
            self.parent().addClass('hidden');
            self.text('Accessors');
            $('.your-messages > li').removeClass('hidden');
        }
    });

    $('.share input').focus(function() {
        $(this).select();
    });
});