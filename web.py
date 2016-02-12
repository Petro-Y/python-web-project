#!cmd /k py -3

from flask import Flask, request, redirect
app = Flask(__name__)

@app.route('/')
def main_page():
    #my projects list....
    #users....
    pass

@app.route('/login', methods=['GET'])
def login_page():
    return '''
Log in:
<form method=POST>
    User: <input name=user><br>
    Password: <input name=password type=password><br>
    <input type=submit>
</form>
or registrate:
<form method=POST>
    User: <input name=user><br>
    Password: <input name=password type=password><br>
    Password (2): <input name=password2 type=password><br>
    E-mail: <input name=email type=email>
    <input type=submit>
</form>
'''

@app.route('/login', methods=['POST'])
def login_page():
    #if password2 and email fields posted, try to registrate....
    #else try to log in.....
    pass

@app.route('/logout')
def logout_page():
    pass

@app.route('/project')
def project_page():
    #show files of the project....
    #show subtasks list....
    pass

@app.route('/subtask')
def subtask_page():
    #show implementations list....
    #my: subtask controls.....
    #others: 'implement...' button....
    pass

if __name__=='__main__':
    app.run()