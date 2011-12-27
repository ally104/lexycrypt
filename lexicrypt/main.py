# -*- coding: utf-8 -*-
import simplejson as json
import time

from httplib2 import Http
from urllib import urlencode

from flask import (Flask, jsonify, redirect,
        render_template, request, session, url_for)

import settings

from lexicrypt import Lexicrypt

app = Flask(__name__)
app.secret_key = settings.SESSION_SECRET

h = Http()
lex = Lexicrypt()


@app.route('/', methods=['GET'])
def main():
    """Default landing page. Loads all
    encrypted messages. If the user has a
    session, check to see if they have access to
    decrypting the message.
    """
    messages = lex.get_messages()
    emessages = []
    if session['lex_email']:
        for message in messages:
            if lex.is_accessible(message['message'],
                                 session['lex_token']):
                message['is_accessible'] = True
            emessages.append(message)
    else:
        emessages = messages
    return render_template('index.html', messages=emessages)


@app.route('/your_messages', methods=['GET'])
def your_messages():
    """Your messages"""
    if not session['lex_email']:
        return redirect(url_for('main'))
    messages = lex.get_messages(session['lex_token'])
    messages_with_decrypted = []
    for message in messages:
        # decrypt each message content
        dmessage = lex.decrypt_message(message['message'],
                                       session['lex_token'])
        message['decrypted'] = dmessage.decode('utf-8')
        messages_with_decrypted.append(message)
    return render_template('your_messages.html',
                           messages=messages_with_decrypted,
                           page='your_messages')


@app.route('/encrypt', methods=['GET'])
def encrypt():
    """Form for encrypting a new message"""
    if not session['lex_email']:
        return redirect(url_for('main'))
    return render_template('encrypt.html', page='encrypt')


@app.route('/set_email', methods=['POST'])
def set_email():
    """Verify via BrowserID and upon success, set
    the email for the user unless it already
    exists and return the token.
    """
    bid_fields = {'assertion': request.form['bid_assertion'],
                  'audience': settings.DOMAIN}
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


@app.route('/set_message', methods=['POST'])
def set_message():
    """Generate the image for this message and return
    the url and image to the user
    """
    if not session['lex_email']:
        return redirect(url_for('main'))
    lex.get_or_create_email(session['lex_email'])
    image_filename = '%s.png' % str(int(time.time()))
    lex.encrypt_message(request.form['message'],
                        'tmp/',
                        image_filename,
                        session['lex_token'])
    return redirect('your_messages')


@app.route('/get_message', methods=['POST'])
def get_message():
    """Decrypt the message from the image url"""
    if not session['lex_email']:
        return redirect(url_for('main'))
    lex.get_or_create_email(session['lex_email'])
    message = lex.decrypt_message(request.form['message'],
                                  session['lex_token'])
    return jsonify({'message': message})


@app.route('/delete_message', methods=['POST'])
def delete_message():
    """Delete the message"""
    if not session['lex_email']:
        return redirect(url_for('main'))
    lex.delete_message(request.form['message'],
                       session['lex_token'])
    return redirect('your_messages')


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
    app.debug = settings.DEBUG
    app.env = 'dev'
    app.run()
