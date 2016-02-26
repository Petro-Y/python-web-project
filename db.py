from sqlite3 import connect

#db_name='project.db'
from settings import db_name
from proj import project_by_name

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
            slave_id int,
            master_id int);
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
    
    #files:
    files=project_by_name(user, project).get_all_files()
    
    #subtasks:
    cur=conn.cursor()
    cur.execute('''
    select slaveuser.name, slave.name from project as slave
    join project_rel on project_rel.slave_id=slave.id
    join project as master on project_rel.master_id=master.id
    join user as slaveuser on slave.user_id=slauser.id
    join user as masteruser on master.user_id=masteruser.id
    where masteruser.name=? and master.name=?
    ''', (user, project))
    subtasks=[row[0]+'/'+row[1] for row in cur]
    cur.close()
    
    #supertasks:
    cur=conn.cursor()
    cur.execute('''
    select masteruser.name, master.name from project as slave
    join project_rel on project_rel.slave_id=slave.id
    join project as master on project_rel.master_id=master.id
    join user as slaveuser on slave.user_id=slauser.id
    join user as masteruser on master.user_id=masteruser.id
    where slaveuser.name=? and slave.name=?
    ''', (user, project))
    supertasks=[row[0]+'/'+row[1] for row in cur]
    cur.close()

    conn.close()
    return dict( user=user, project=project,
            is_subtask=is_subtask, files=files, 
            subtasks=subtasks, supertasks=supertasks)
                
def user_exists(username):
    pass #true if user exists....                
def email_exists(email):
    pass #true if user exists....
def add_user(user, password, email):
    pass
def check_user(user, password):
    pass