import os
from os import path
import datetime
from flask import Flask, request, url_for, render_template, redirect, session

SPOOL_DIR = '/opt/onote/spool'
PASSWD_FILE = '/home/user/PycharmProjects/onote/conf/passwd'
SESSION_TIMEOUT = 600

static_dir = os.path.abspath('.')

app = Flask(__name__, template_folder=static_dir)
app.config.update(SECRET_KEY=b'\xaax\xc5\xa6k\xc60\xb9x\xd65\xc5fdz\xb3')

def an_validate(v, l = 64):
    if v is None:
        return None
    if len(v) > l:
        return None
    if not v.isalnum():
        return None
    return v

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('login_timeout', None)
    session.pop('login_invalid', None)
    session.pop('login_failed', None)
    session.pop('login_note', None)
    session.pop('login_auth', None)

    """Login Form"""
    if session.get('username'):
        return 'FUCK YOU: LOGGED IN!'

    name = an_validate(request.form['user'], 32)
    passw = request.form['pass']
    if name is None or passw is None:
        session['login_invalid'] = True
        return render_template('sign-in.html')

    try:
        with open(PASSWD_FILE) as f:
            if name + ':' + passw in f.read():
                session['username'] = name
                re = request.form.get('remember-me')
                session['remember'] = False
                if re is not None:
                    session['remember'] = True
                return redirect('/msg')
            session['login_invalid'] = True
            return render_template('sign-in.html')
    except:
        session['login_failed'] = True
        return render_template('sign-in.html')


@app.route('/show', methods=['GET', 'POST'])
def show():
    if not session.get('username'):
        session['login_auth'] = True
        return render_template('sign-in.html')
    if request.form.get('show') is not None:
        session['show'] = True
        return redirect('/msg')

    return 'FUCK YOU: ERRORKA REQUEST!'

@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    session.pop('id', None)
    session.pop('attempt', None)
    session['used'] = datetime.datetime.now().timestamp()
    return redirect('/')

@app.route("/msg")
def message():
    #session.clear()
    """ Session control"""
    if request.method == 'GET':
        if request.args.get('id') is not None:
            session['id'] = request.args['id']

    msg = an_validate(session.get('id'))
    if msg is None:
        return 'FUCK YOU: MSG INVALID'

    if session.get('used') is not None:
        if datetime.datetime.now().timestamp() - session['used'] > SESSION_TIMEOUT:
            remember = session.get('remember-me')
            session.clear()
            if remember is not None:
                session['remember'] = remember
            session['id'] = msg
            session['login_timeout'] = True
            return render_template('sign-in.html')
    session['used'] = datetime.datetime.now().timestamp()

    if session.get('username'):
        user = session['username']
    else:
        session['login_note'] = True
        return render_template('sign-in.html')

    remember = session.get('remember')

    msgfile = path.join(SPOOL_DIR, user)
    msgfile = path.join(msgfile, msg)
    if not path.exists(msgfile):
        msgfile = path.join(SPOOL_DIR, msg)

    if not path.exists(msgfile):
        return 'FUCK YOU: NO MSG FILE!'
    if path.exists(msgfile + '.r'):
        if path.exists(msgfile + '.a'):
            os.remove(msgfile + '.a')
        return 'FUCK YOU: NAH POLUCHISH MSG!'

    if not session.get('show'):
        if path.exists(msgfile + '.a'):
            return render_template('show-note.html', attempt=1)
        else:
            return render_template('show-note.html')

        return render_template('show-note.html')

    session.pop('show', None)

    f = open(msgfile)
    msgdata = f.read()
    f.close()
    if path.exists(msgfile + '.a'):
        os.remove(msgfile + '.a')
        open(msgfile + '.r', 'a').close()

    if not remember:
        session.clear()

    return msgdata


@app.route("/")
def home():
    return 'HOME'

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=8071)
