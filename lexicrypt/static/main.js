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

    $('.accessors a.delete').click(function(ev) {
        ev.preventDefault();
        var self = $(this);
        var bottom = (26 * self.parent().find('li.email').length) + (16 * self.parent().find('li.email').length);
        $.ajax({
            url: '/remove_email',
            data: { "message": self.data('message'), "email": self.data('email') },
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                bottom = bottom - 16;
                console.log(bottom);
                self.closest('.accessors').css({'bottom': '-' + bottom + 'px'});
                self.parent().remove();
            }
        });
    });

    $('.accessors li.toggle').click(function() {
        var self = $(this);
        var bottom = 26;
        if(self.parent().hasClass('hidden')) {
            // calculate how far the bottom should be based on
            // how many emails there are.
            bottom = bottom * self.parent().find('li.email').length + bottom;
            self.parent().css({'bottom': '-' + bottom + 'px'});
            self.parent().removeClass('hidden');
            self.text('Hide');
        } else {
            self.parent().css({'bottom': '-26px'});
            self.parent().addClass('hidden');
            self.text('Accessors');
        }
    });
});