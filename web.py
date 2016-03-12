#!cmd /k py -3

from db import *
import proj
from flask import Flask, request, redirect, render_template, session
from settings import secret_key
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.secret_key=secret_key
socketio = SocketIO(app)

@app.route('/')
def main_page():
    user=session['current_user'] if 'current_user' in session else None
    return redirect(user+'/' if user else 'login')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/ws', methods=['GET'])
def ws_page():
    return render_template('ws.html')

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    emit('my response', {'data': 'hello'})

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
    #if password2 and email fields posted, try to register (and log in)
    #
    user=request.form['user']
    password=request.form['password']
    password2=request.form['password2']
    email=request.form['email']
    if password!=password2: 
        return render_template('login.html', error='Вкажіть один і той же пароль двічі!',
                               user=user, email=email, register=True)
    elif user_exists(user): 
        return render_template('login.html', error="Користувача з таким ім'ям уже зареєстровано!",
                               user=user, email=email, register=True)
    elif email_exists(email): 
        return render_template('login.html', error="Потрібна унікальна адреса електронної пошти!",
                               user=user, email=email, register=True)
    add_user(user, password, email)
    session['current_user']=user
    return redirect('./')


@app.route('/logout')
def logout_page():
    del session['current_user']
    return redirect('./')
    
@app.route('/<user>/<project>/<path:fname>', methods=['GET'])
def file_page(user, project, fname):
    project_vfs=proj.project_by_name(user, project)
    content=''.join(project_vfs.load(fname))
    #if ?mode=raw, show content as plain text:
    try:
        if request.args.get('mode')=='raw':
            return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception:
        pass
    return render_template('file.html', f=content, fname=fname, user=user, project=project)
    
    
@app.route('/<user>/<project>/<path:fname>', methods=['POST'])
def file_post(user, project, fname):
    content=request.form['content']
    if session['current_user']!=user:
        return render_template('file.html', f=content, fname=fname, user=user, project=project,
               error='Ви не маєте прав редагувати файл. Створіть відгалуження проекту чи реалізацію підзадачі')
        #show error message (fork/implement?)
    #save changes:
    project_vfs=proj.project_by_name(user, project)
    project_vfs.save(fname, content)
    return redirect('.')

@app.route('/<user>/<project>/', methods=['GET'])
def project_page(user, project):
    #project_vfs=proj.project_by_name(user, project)
    #if mode=='zip': generate zip archive.....
    #show files of the project
    #show subtasks list
    return render_template('project.html',
        is_current=session['current_user']==user if 'current_user' in session else False,
        **project_data(user, project))


@app.route('/<user>/<project>/', methods=['POST'])
def project_post(user, project):
    pass#upload zip, or upload test-report......

@app.route('/<user>/')
def user_page(user):
    return render_template('user.html', **user_data(user))


#@app.route('/subtask')
def subtask_page():
    #show implementations list....
    #my: subtask controls.....
    #others: 'implement...' button....
    pass

if __name__=='__main__':
    socketio.run(app)
