# -*- coding: utf-8 -*-
import md5
from functools import wraps
from flask import redirect, session, url_for

import settings


def authenticated(f):
    """Check if user is logged in"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('lex_email'):
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return decorated

def is_decryptable(lex, message, session):
    """If message is decryptable, add
    the extra flags
    """
    message['share'] = '%s%s' % (settings.DOMAIN, url_for('message', id=str(message['_id'])))
    if lex.is_accessible(message['message'],
                         session.get('lex_token')):
        email = str(md5.new(lex.get_email_by_token(message['token'])).hexdigest())
        gravatar = 'http://www.gravatar.com/avatar/%s?s=50' % email
        message['is_accessible'] = True
        message['gravatar'] = gravatar

    return message
