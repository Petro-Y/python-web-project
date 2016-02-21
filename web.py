#!cmd /k py -3

from flask import Flask, request, redirect, render_template
app = Flask(__name__)
app.secret_key='ssdhgj_mdzj'

@app.route('/')
def main_page():
    #users....
    user='None'
    return redirect(user if user else 'login')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    #try to log in.....
    return redirect('./')

@app.route('/register', methods=['POST'])
def register_post():
    #if password2 and email fields posted, try to register (and log in)....
    return redirect('./')


@app.route('/logout')
def logout_page():
    pass

@app.route('/<user>/<project>/')
def project_page(user, project):
    #show files of the project....
    #show subtasks list....
    files=['file1.c', 'file2.c', 'file3.html']
    subtasks=['st1', 'st2']
    supertasks=['project']
    return render_template('project.html', user=user, project=project,
                files=files, subtasks=subtasks, supertasks=supertasks)
    # return '''
    # <h1>User: %s</h1>
    # <h2>Project: %s<h2>
    # '''% (user, project)

@app.route('/<user>/')
def user_page(user):
    #user's projects list....
    return render_template('user.html', user=user)
    # return '''
    # <h1>User: %s</h1>
    # '''%user



@app.route('/subtask')
def subtask_page():
    #show implementations list....
    #my: subtask controls.....
    #others: 'implement...' button....
    pass

if __name__=='__main__':
    app.run()