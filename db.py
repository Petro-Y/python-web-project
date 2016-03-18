#!py -3 -i
from sqlite3 import connect
from hashlib import md5
import os

from proj import project_by_name
from settings import db_name, passhashsecret

def create_db():
    try:
        os.unlink(db_name)
    except:
        pass
    conn=connect(db_name)
    cur=conn.cursor()
    cur.executescript('''
    create table user(
            id integer primary key autoincrement,
            name char(50),
            passhash char(32),
            email char(100));
    create table project(
            id integer primary key autoincrement,
            name char(50),
            user_id int,
            status int,
            implementation_id int,''' #what's this? supertask?...
            '''changed datetime);
    create table project_rel(
            id integer primary key autoincrement,
            slave_id int,
            master_id int);
    create table status(
            id int,
            category int,
            name char(20));
    insert into status values
            (0, 0, 'project'),
            (1, 0, 'test_project'),
            (2, 1, 'subtask'),
            (3, 1, 'subtask_done'),
            (4, 1, 'subtask_cancelled'),
            (5, 2, 'qa_task');
    create table test(
            id int,
            report text,
            build_id int
            );
    create table build(
           id int,
           name char(120),
           project_id int,
           impl_id int,
           created datetime
           );
    /* create table build_impl(
           build_id int,
           impl_id int
           ); */
    create table qa_watch(
           qa_user_id int,
           project_id int
           );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    add_user('boss', 'boss', 'boss@example.com')
    add_user('slave', 'slave', 'slave@example.com')
    add_user('qa', 'qa', 'qa@example.com')

def project_data(user, project):
  #print('project_data', user, project)
  try:
    conn=connect(db_name); cur=conn.cursor()
    cur.execute('''
    select status.category from project
    join user on project.user_id=user.id
    join status on project.status=status.id
    where user.name=? and project.name=?
    ''', (user, project))
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
  except:
    #print('project_data problems...')
    return dict( user=user, project=project, error='Stub mode (DB is inaccessible)',
        files=['file1.c', 'file2.c', 'file3.html'],#get them from project_vfs........
        subtasks=['st1', 'st2'],#project_vfs.get_subtasks() ......
        supertasks=['project'],#project_vfs.get_supertasks() .....,
        reports=[('QA', '22.03.2016', 'Deadline error: nothing implemented!!!')],
        is_subtask=project.startswith(('st', 'subtask')))


def user_data(username):
  try:
    #.....
    conn=connect(db_name)
    cur=conn.cursor()
    projects=[p for p, in cur.execute('''
        select name from project
        join user on user.id=project.user_id
        join status on project.status=status.id
        where user.name=? and status.category=0
    ''', (username,))]
    subtasks=[p for p, in cur.execute('''
        select name from project
        join user on user.id=project.user_id
        join status on project.status=status.id
        where user.name=? and status.category=1
    ''', (username,))]
    #qa tasks: 
    #find builds w/o test report for all watched projects....
    qatasks=[list(row) for row in cur.execute('''
            with recursive ancestor as 
                (select project_id from qa_watch
                union select slave_id from project_rel 
                join ancestor on ancestor.project_id=project_rel.master_id)
            select * from build 
            join ancestor on ancestor.project_id=build.project_id
            where build.id not in (select build_id from test)
    ''', (username,))]
    #find list of implementations for each of them.....
    for qatask in qatasks:
        
        pass#...
    
    #reports....
    return dict(user=username, projects=projects, subtasks=subtasks, quatasks=qatasks, reports=reports)
  except:
    return dict(user=username, error='Stub mode (DB is inaccessible)',
                projects=['project1', 'project2'],
                subtasks=['subtask1', 'subtask2'],
                qatasks=[('build/ghg676761', 'user1/project1', 'user2/impl1'), ('user1/project1', 'user1/project1')])


def user_exists(username):
    try:
        conn=connect(db_name)
        cur=conn.cursor()
        cur.execute('''
        select name from user where name=?
        ''', (username,))
        for row in cur:
            print('user', username, 'found')
            return True
        print('user', username, 'not found')
        return False
    finally:
        cur.close() 
        conn.close()
    
def email_exists(email):
    try:
        conn=connect(db_name)
        cur=conn.cursor()
        cur.execute('''
        select email from user where email=?
        ''', (email,))
        for row in cur:
            return True
        return False
    finally:
        cur.close() 
        conn.close()

def get_passhash(user, password):
    return md5((user+password+passhashsecret).encode()).hexdigest()

def add_user(user, password, email):
    passhash=get_passhash(user, password)
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
    insert into user (name, passhash, email) values (?, ?, ?);
    ''', (user, passhash, email))
    conn.commit()
    cur.close() 
    conn.close()
        
def check_user(user, password):
    try:
        passhash=get_passhash(user, password)
        conn=connect(db_name)
        cur=conn.cursor()
        cur.execute('''
        select * from user where name=? and passhash=?
        ''', (user, passhash))
        for row in cur:
            return True
        return False
    finally:
        cur.close() 
        conn.close()