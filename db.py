from sqlite3 import connect

#db_name='project.db'
from settings import db_name

def create_db():
    conn=connect(db_name)
    cur=conn.cursor()
    cur.executescript('''
    create table user
            (id int primary key auto increment,
            name char(50),
            passhash char(20));
    create table project
            (id int primary key auto increment,
            user_id int,
            status int,''' # (0=project, 1=test_project, 2=subtask, 3=subtask_done, 4=subtask_cancelled)
    '''
            implementation_id int);
    create table project_rel
            (id int primary key auto increment,
            project_id int,
            base_id int);
    create table status
            (id int,
            name char(20));
    ''')
    conn.commit()
    cur.close()
    conn.close()

def project_data(username, project):
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
    select status from project
    join user on project.user_id=user.id
    where 
    ''')#......
    for row in cur:
        #is_subtask: select status from project
        pass
    cur.close()


    conn.close()
    '''return dict( user=user, project=project,
                           is_subtask=False,
                files=files, subtasks=subtasks, supertasks=supertasks)'''
    pass
                
def user_exists(username):
    pass #true if user exists....                
def email_exists(email):
    pass #true if user exists....
def add_user(user, password, email):
    pass
def check_user(user, password):
    pass