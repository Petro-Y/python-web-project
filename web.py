#!cmd /k py -3

from db import *
from flask import Flask, request, redirect, render_template, session
app = Flask(__name__)
app.secret_key='ssdhgj_mdzj'

@app.route('/')
def main_page():
    user=session['current_user'] if 'current_user' in session else None
    return redirect(user+'/' if user else 'login')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    #try to log in:
    user=request.form['user']
    password=request.form['password']
    #check user and password (show login page with error message if user/password is wrong:
    if check_user(user, password):
        session['current_user']=user
    else:
        return render_template('login.html', error="Неправильний логін чи пароль!", user=user)
    return redirect('./')

@app.route('/register', methods=['POST'])
def register_post():
    #if password2 and email fields posted, try to register (and log in)....
    #
    user=request.form['user']
    password=request.form['password']
    password2=request.form['password2']
    email=request.form['email']
    if password!=password2: 
        return render_template('login.html', error='Вкажіть один і той же пароль двічі!', user=user, email=email, register=True)
    elif user_exists(user): 
        return render_template('login.html', error="Користувача з таким ім'ям уже зареєстровано!", user=user, email=email, register=True)
    elif email_exists(email): 
        return render_template('login.html', error="Потрібна унікальна адреса електронної пошти!", user=user, email=email, register=True)
    add_user(user, password, email)
    session['current_user']=user
    return redirect('./')


@app.route('/logout')
def logout_page():
    del session['current_user']
    return redirect('./')
    
@app.route('/<user>/<project>/<path:fname>', methods=['GET'])
def file_page(user, project, fname):
    #get project....
    f=''.join(project.load(fname))
    return render_template('file.html', f=f, fname=fname)
    
    
@app.route('/<user>/<project>/<path:fname>', methods=['GET'])
def file_post(user, project, fname):
    #save changes.....
    return redirect('.')

@app.route('/<user>/<project>/')
def project_page(user, project):
    #show files of the project....
    #show subtasks list....
    files=['file1.c', 'file2.c', 'file3.html']
    subtasks=['st1', 'st2']
    supertasks=['project']
    return render_template('project.html', user=user, project=project,
                           is_subtask=False,
                files=files, subtasks=subtasks, supertasks=supertasks)


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