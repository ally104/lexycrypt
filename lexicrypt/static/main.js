$(function() {
    $('#login').click(function() {
        navigator.id.getVerifiedEmail(function(assertion) {
            if(assertion) {
                $('form input').val(assertion);
                $('form').submit();
            } else {
                alert('not logged in');
            }
        });
    });

    $('a.delete').click(function(ev) {
        ev.preventDefault();
    });
});