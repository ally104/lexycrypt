# -*- coding: utf-8 -*-
import simplejson as json
import time

from httplib2 import Http
from urllib import urlencode

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

import settings

from lexicrypt import Lexicrypt

app = Flask(__name__)
app.secret_key = settings.SESSION_SECRET

h = Http()
lex = Lexicrypt()


@app.route('/', methods=['GET'])
def main():
    """Default landing page"""
    if session['lex_token']:
        messages = lex.get_messages(session['lex_token'])
        messages_with_decrypted = []
        for message in messages:
            # decrypt each message content
            dmessage = lex.decrypt_message(message['message'], session['lex_token'])
            message['decrypted'] = dmessage.decode('utf-8')
            messages_with_decrypted.append(message)
        return render_template('index.html', messages=messages_with_decrypted)
    else:
        return render_template('index.html', page='main')

@app.route('/set_email', methods=['POST'])
def set_email():
    """Verify via BrowserID and upon success, set
    the email for the user unless it already
    exists and return the token.
    """
    bid_fields = { 'assertion': request.form['bid_assertion'],
                   'audience': settings.DOMAIN }
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    resp, content = h.request('https://browserid.org/verify',
                              'POST',
                              body=urlencode(bid_fields),
                              headers=headers)
    bid_data = json.loads(content)
    if bid_data['status'] == 'okay' and bid_data['email']:
        # authentication verified, now get/create the
        # lexicrypt email token
        lex.get_or_create_email(bid_data['email'])
        session['lex_token'] = lex.token
        session['lex_email'] = bid_data['email']

    return render_template('index.html', page='main')

@app.route('/get_accessible', methods=['POST'])
def get_accessible():
    """Check to see if the user's token is one in the
    accessor list for this image
    """
    try:
        if lex.is_accessible(request.form['message'], request.form['lex_token']):
            result = { "message": "Access granted", "status": 200 }
            return jsonify(result)
        else:
            result = { "message": "Access denied", "status": 401 }
            return jsonify(result)
    except TypeError, ValueError:
        result = { "message": "Access denied", "status": 401 }
        return jsonify(result)

@app.route('/set_message', methods=['POST'])
def set_message():
    """Generate the image for this message and return
    the url and image to the user
    """
    if not session['lex_email']:
        return redirect(url_for('main'))
    lex.get_or_create_email(session['lex_email'])
    image_filename = '%s.png' % str(int(time.time()))
    image = lex.encrypt_message(request.form['message'],
                                'static/generated/',
                                image_filename,
                                session['lex_token'])
    
    return render_template('index.html', image=image)

@app.route('/get_message', methods=['POST'])
def get_message():
    """Decrypt the message from the image url"""
    if not session['lex_email']:
        return redirect(url_for('main'))
    lex.get_or_create_email(session['lex_email'])
    message = lex.decrypt_message(request.form['message'],
                                  session['lex_token'])
    return render_template('index.html', message=message.decode('utf-8'))

@app.route('/delete_message', methods=['POST'])
def delete_message():
    """Delete the message"""
    if not session['lex_email']:
        return redirect(url_for('main'))
    lex.delete_message(request.form['message'],
                       session['lex_token'])
    return redirect(url_for('main'))

@app.route('/add_email', methods=['POST'])
def add_email():
    """Add an email to the access list"""
    if not session['lex_email']:
        return redirect(url_for('main'))
    lex.add_email_accessor(request.form['message'],
                           request.form['email'],
                           session['lex_token'])
    return render_template('index.html')

@app.route('/logout', methods=['GET'])
def logout():
    """Log the user out"""
    session['lex_token'] = None
    session['lex_email'] = None
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.debug = True
    app.run()