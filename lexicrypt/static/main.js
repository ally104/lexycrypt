$(function() {
    var emailItemLength = 16;

    /* Authenticatication for Persona */
    $('#login').click(function(ev) {
      ev.preventDefault();
      navigator.id.request();
    });

    $('#logout').click(function(ev) {
      ev.preventDefault();
      navigator.id.logout();
    });

    navigator.id.watch({
      loggedInUser: currentUser,
      onlogin: function(assertion) {
        $.ajax({
          type: 'POST',
          url: '/set_email',
          data: { assertion: assertion },
          success: function(res, status, xhr) {
            window.location.reload();
          },
          error: function(res, status, xhr) {
            console.log('Login failure:' + res.status + ': ' + res.statusText);

            // Remove any old notices
            $('.notice.sign-in-error').remove();

            var message = $('<div></div>');
            message.addClass('notice error dismissable sign-in-error');
            message.html('We were unable to sign you in. Please try again.');

            message.on('click', function() {
              $(this).fadeOut(600, function() {
                $(this).remove();
              });
            });

            message.hide();
            $('#main-notices').prepend(message);

            message.fadeOut(0, function() {
              message.fadeIn(400);
            });
          }
          });
        },
        onlogout: function() {
          $.ajax({
            type: 'POST',
            url: '/logout',
            success: function(res, status, xhr) {
              window.location.reload();
            },
            error: function(res, status, xhr) {
              console.log('Logout failure: ' + res.status + ': ' + res.statusText);
            }
          });
        }
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
