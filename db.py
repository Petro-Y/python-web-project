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
            name char(50),
            user_id int,
            status int,
            implementation_id int);
    create table project_rel
            (id int primary key auto increment,
            project_id int,
            base_id int);
    create table status
            (id int,
            category int,
            name char(20));
    insert into status values
            (0, 0, 'project'),
            (1, 0, 'test_project'),
            (2, 1, 'subtask'),
            (3, 1, 'subtask_done'),
            (4, 1, 'subtask_cancelled),
            (5, 2, 'qa_task');
    ''')
    conn.commit()
    cur.close()
    conn.close()

def project_data(username, project):
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
    select status.category from project
    join user on project.user_id=user.id
    join status on project.status=status.id
    where user.name=? and project.name=?
    ''', (username, project))
    for row in cur:
        #is_subtask: select status from project
        is_subtask=row[0]==1
    cur.close()
    #files.....
    
    #subtasks....
    cur=conn.cursor()
    cur.execute('''
    select ....
    ''', (project,))
    for row in cur:
        pass
    cur.close()
    #supertasks....

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