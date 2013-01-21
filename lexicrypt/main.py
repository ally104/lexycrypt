# -*- coding: utf-8 -*-
import simplejson as json
import time

import browserid
from httplib2 import Http
from urllib import urlencode

from flask import (Flask, jsonify, redirect,
                   render_template, request, session, url_for)

import settings

from helper import *
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

    for message in messages:
        emessages.append(is_decryptable(lex, message, session))

    return render_template('index.html', messages=emessages)


@app.route('/disclaimer', methods=['GET'])
def disclaimer():
    """Disclaimer page."""
    messages = lex.get_messages()

    return render_template('disclaimer.html')


@app.route('/message/<id>', methods=['GET'])
def message(id):
    """Single message display."""
    message = lex.get_message(id)
    if request.args.get('embedded'):
        embedded = True
    else:
        embedded = False
    if message:
        message = is_decryptable(lex, message, session)
        return render_template('message.html', message=message, embedded=embedded)
    else:
        return render_template('404.html')


@app.route('/your_messages', methods=['GET'])
@authenticated
def your_messages():
    """Your messages."""
    messages = lex.get_messages(session['lex_token'])
    messages_with_decrypted = []

    for message in messages:
        # decrypt each message content
        emails = []
        dmessage = lex.decrypt_message(message['message'],
                                       session.get('lex_token'))
        message['decrypted'] = dmessage.decode('utf-8')
        for accessor in message['accessors']:
            if accessor != session['lex_token']:
                user = lex.db.users.find_one({"token": accessor})
                emails.append(user['email'])
        message['emails'] = emails
        message['share'] = '%s%s' % (settings.SITE_URL, url_for('message', id=str(message['_id'])))
        messages_with_decrypted.append(message)
    return render_template('your_messages.html',
                           messages=messages_with_decrypted,
                           page='your_messages')


@app.route('/encrypt', methods=['GET'])
@authenticated
def encrypt():
    """Form for encrypting a new message."""
    return render_template('encrypt.html', page='encrypt')


@app.route('/set_email', methods=['POST'])
def set_email():
    """Verify via Persona and upon success, set
    the email for the user unless it already
    exists and return the token.
    """
    data = browserid.verify(request.form['assertion'],
                            settings.SITE_URL)
    email = data['email']

    # authentication verified, now get/create the
    # lexicrypt email token
    lex.get_or_create_email(email)
    session['lex_token'] = lex.token
    session['lex_email'] = email
    return redirect(url_for('main'))


@app.route('/set_message', methods=['POST'])
@authenticated
def set_message():
    """Generate the image for this message and return
    the url and image to the user.
    """
    lex.get_or_create_email(session['lex_email'])
    image_filename = '%s.png' % str(int(time.time()))
    lex.encrypt_message(request.form['message'],
                        'tmp/',
                        image_filename,
                        session.get('lex_token'))
    return redirect(url_for('your_messages'))


@app.route('/get_message', methods=['POST'])
@authenticated
def get_message():
    """Decrypt the message from the image url."""
    lex.get_or_create_email(session['lex_email'])
    message = lex.decrypt_message(request.form['message'],
                                  session.get('lex_token'))
    return jsonify({'message':message})


@app.route('/delete_message', methods=['POST'])
@authenticated
def delete_message():
    """Delete the message."""
    lex.delete_message(request.form['message'],
                       session['lex_token'])
    return redirect(url_for('your_messages'))


@app.route('/remove_email', methods=['POST'])
@authenticated
def remove_email():
    """Remove an email from the accessor list."""
    lex.remove_email_accessor(request.form['message'],
                              request.form['email'],
                              session.get('lex_token'))
    return jsonify({'message':'removed email'})


@app.route('/add_email', methods=['POST'])
@authenticated
def add_email():
    """Add an email to the access list."""
    lex.add_email_accessor(request.form['message'],
                           request.form['email'],
                           session.get('lex_token'))
    return jsonify({'email':request.form['email']})


@app.route('/logout', methods=['POST'])
def logout():
    """Log the user out."""
    session.pop('lex_token', None)
    session.pop('lex_email', None)
    return redirect(url_for('main'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


@app.errorhandler(500)
def something_broke(error):
    return render_template('500.html')


if __name__ == '__main__':
    app.debug = settings.DEBUG
    app.run()
