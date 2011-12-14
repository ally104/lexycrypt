from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flaskext.jsonify import jsonify

from lexicrypt import Lexicrypt

app = Flask(__name__)


@app.route('/')
@jsonify
def main():
    return { 'message': 'landed on homepage' }

@app.route('/set_email', methods=['POST'])
@jsonify
def set_email():
    """
    Set the email for the user unless it already
    exists and return the token
    """ 
    lex = Lexicrypt()
    lex.get_or_create_email(request.form['email'])
    return { 'token': lex.token }

if __name__ == '__main__':
    app.run()