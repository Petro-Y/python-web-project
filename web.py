#!cmd /k py -3

from flask import Flask, request, redirect, render_template, session
from flask_socketio import SocketIO, emit
from zipfile import ZipFile
from werkzeug import secure_filename
import os


from db import *
import proj
from proj import project_by_name, project_data
from settings import secret_key, upload_folder, rootdir



app = Flask(__name__)
app.secret_key=secret_key
app.config['UPLOAD_FOLDER']=upload_folder
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
    content=''; error=''
    try:
        project_vfs=proj.project_by_name(user, project)
        content=''.join(project_vfs.load(fname))
    except:
        error='No such file exists'
    #if ?mode=raw, show content as plain text:
    try:
        if request.args.get('mode')=='raw':
            return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception:
        pass
    return render_template('file.html', f=content, fname=fname, user=user, project=project, error=error)
    
    
@app.route('/<user>/<project>/<path:fname>', methods=['POST'])
def file_post(user, project, fname):
    print(user, project, fname)
    content=request.form['content']
    print(user, project, fname, 'content is OK')
    if session['current_user']!=user:
        return render_template('file.html', f=content, fname=fname, user=user, project=project,
               error='Ви не маєте прав редагувати файл. Створіть відгалуження проекту чи реалізацію підзадачі')
        #show error message (fork/implement?)
    #save changes:
    print(user, project, fname, 'user check is OK')
    project_vfs=proj.project_by_name(user, project)
    print(user, project, fname, 'project_by_name is OK')
    project_vfs.save(fname, content)
    print(user, project, fname, 'save is OK')
    return redirect('.')

@app.route('/<user>/<project>/', methods=['GET'])
def project_page(user, project):
    #project_vfs=proj.project_by_name(user, project)
    try:
        if request.args.get('mode')=='zip':
            # see https://docs.python.org/3/library/zipfile.html
            # generate zip archive (in /static/download directory)........
            zfname=rootdir+'static/'+user+'/'+project+'.zip'
            pr=project_by_name(user, project)
            with ZipFile(zfname, 'w') as zf:
                for filename in pr.get_all_files():
                    zf.writestr(filename, ''.join(pr.load(filename)).encode())
            # and download it:
            return redirect(zfname)
            pass
    except:
        pass
    #show files of the project
    #show subtasks list
    return render_template('project.html',
        is_current=session['current_user']==user if 'current_user' in session else False,
        **project_data(user, project))


@app.route('/<user>/<project>/', methods=['POST'])
def project_post(user, project):
    "upload zip, or upload test-report......"
    print('POST', user, project)
    action=request.form['action']
    print('    ', action, user, project)
    if action=='send_report':
        report=request.form['testreport']
        print('test report:', report)
        #add report to db....
        try:
            socketio.emit('qa_report '+user+'/'+project, {'text': report})#...
            # see https://flask-socketio.readthedocs.org/en/latest/
            # see http://stackoverflow.com/questions/30124701/how-to-emit-websocket-message-from-outside-a-websocket-endpoint
            print('emit is ok')
        except Exception as e:
            print(e)
    elif action=='upload':
        # upload zip file ....
        # see http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
        zf=request.files['zipfile']
        if zf:
            # extract it....
            filename = secure_filename(zf.filename)
            zf.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with ZipFile(filename) as zf:
                zf.extractall()#prepare target path....
                # (create new folder for extracted, then remove old files and move it on their place)....
    elif action=='build':
        target_user, target_project=request.form['target'].split('/', 1)
        #  create test build ...
        # impl (user, project) = current project
        # project (user, project) = target project
        buildname='build/'+proj.build(target_user, target_project, impls)
        #  emit message to QA...
        for qa in get_qa_list(user, project):
            socketio.emit('qa_request '+qa, {'build': buildname})
    elif action=='integrate':
        #integrate current implementation into target project....
        pass
    elif action=='find_subtasks':
        proj.find_subtasks(user, project)
    elif action=='add_file':
        return redirect('/'+user+'/'+project+'/'+request.form['filename'])
    return redirect('/'+user+'/'+project)


@app.route('/<user>/', methods=['GET'])
def user_page(user):
    try:
        if request.args.get('newproject'):
            add_project(user, request.args.get('newproject'))
    except:
        pass
    return render_template('user.html', **user_data(user))

try:
    from settings import enable_reset
    if enable_reset:
        @app.route('/reset')
        def reset_page():
            create_db()
            return '''DB creation/reset complete.<br>
            To prevent this in future, remove 'enable_reset=True' from settings.py and restart the server.'''
except:
    pass

if __name__=='__main__':
    socketio.run(app, host='0.0.0.0')
