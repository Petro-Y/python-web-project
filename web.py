#!cmd /k py -3

from flask import Flask, request, redirect
app = Flask(__name__)
app.secret_key='ssdhgj_mdzj'

@app.route('/')
def main_page():
    #users....
    user='None'
    return redirect(user if user else 'login')

@app.route('/login', methods=['GET'])
def login_page():
    return '''
Log in:
<form method=POST>
    User: <input name=user><br>
    Password: <input name=password type=password><br>
    <input type=submit>
</form>
or register:
<form method=POST>
    User: <input name=user><br>
    Password: <input name=password type=password><br>
    Password (2): <input name=password2 type=password><br>
    E-mail: <input name=email type=email>
    <input type=submit>
</form>
'''

@app.route('/login', methods=['POST'])
def login_post():
    #if password2 and email fields posted, try to registrate....
    #else try to log in.....
    return redirect('.')

@app.route('/logout')
def logout_page():
    pass

@app.route('/<user>/<project>/')
def project_page(user, project):
    #show files of the project....
    #show subtasks list....
    return '''
    <h1>User: %s</h1>
    <h2>Project: %s<h2>
    '''% (user, project)

@app.route('/<user>/')
def user_page(user):
    #user's projects list....
    return '''
    <h1>User: %s</h1>
    '''%user



@app.route('/subtask')
def subtask_page():
    #show implementations list....
    #my: subtask controls.....
    #others: 'implement...' button....
    pass

if __name__=='__main__':
    app.run()