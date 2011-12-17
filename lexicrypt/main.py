import simplejson as json

from urllib import urlencode

from httplib2 import Http

from flask import abort, flash, Flask, g, redirect, render_template, request, session, g, url_for
from flaskext.jsonify import jsonify

import settings

from lexicrypt import Lexicrypt

app = Flask(__name__)
app.secret_key = settings.SESSION_SECRET

h = Http()
lex = Lexicrypt()


@app.route('/', methods=['GET'])
def main():
    """
    Default landing page
    """
    return render_template('index.html', page='main')

@app.route('/set_email', methods=['POST'])
@jsonify
def set_email():
    """
    Verify via BrowserID and upon success, set
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
    if bid_data['status'] == 'okay' and bid_data['issuer'] == 'browserid.org':
        # authentication verified, now get/create the
        # lexicrypt email token
        lex.get_or_create_email(bid_data['email'])
        return { 'token': lex.token }
    else:
        redirect(url_for('main'))

if __name__ == '__main__':
    app.run()