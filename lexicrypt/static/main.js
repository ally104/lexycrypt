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

    $('body').on('click', '#message', function() {
       $('#message').hide(); 
    });

    $('.accessors').on('click', 'a.delete', function(ev) {
        ev.preventDefault();
        var self = $(this);
        var bottom = (26 * self.closest('.accessors').find('li.email').length)+
                     self.closest('.accessors').find('li.email').length + 33;
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

            bottom = (bottom * self.parent().find('li.email').length)+
                     self.parent().find('li.email').length + bottom + 34;
            self.parent().css({'bottom': '-' + bottom + 'px'});
            self.closest('.your-messages > li').addClass('selected');
            self.parent().removeClass('hidden');
            self.text('Hide');
        } else {
            self.parent().css({'bottom': '-26px'});
            self.parent().addClass('hidden');
            self.text('Edit Email Access');
            $('.your-messages > li').removeClass('hidden');
        }
    });

    $('.add-email button').click(function() {
        var self = $(this);
        var bottom = (26 * (self.closest('.accessors').find('li.email').length + 1))+
                     self.closest('.accessors').find('li.email').length + 61;
        var message = self.closest('li.selected').find('img').attr('src');
        var email = self.closest('li.add-email').find('input');
        $.ajax({
            url: '/add_email',
            data: { "message": message, "email": email.val() },
            type: 'POST',
            dataType: 'json',
            success: function(data) {
                var email_link = $('<a href="#" class="delete" data-message="'+message+
                                   '" data-email="'+data['email']+'">x</a>');
                var email_el = $('<li class="email"></li>');
                email_el.append(data['email']).append(email_link);
                self.closest('.accessors').css({'bottom': '-' + bottom + 'px'});
                email_el.insertBefore(self.closest('.accessors').find('.toggle'));
                email.val('');
            }
        }); 
    });

    $('.share input, .embed input').focus(function() {
        $(this).select();
    });
});