# -*- coding: utf-8 -*-
from functools import wraps
from flask import redirect, session, url_for


def authenticated(f):
    """Check if user is logged in"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('lex_email'):
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return decorated
