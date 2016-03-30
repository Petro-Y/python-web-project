#!py -3 -i
from sqlite3 import connect
from hashlib import md5
import os

#from proj import project_by_name
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
            (5, 2, 'qa_task'),
            (6, 0, 'implementation');
    create table test(
            id integer primary key autoincrement,
            report text,
            build_id int
            );
    create table build(
           id integer primary key autoincrement,
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
    else:
        is_subtask=False
    cur.close()
    
    #files:
    #files=project_by_name(user, project).get_all_files()
    
    #subtasks:
    cur=conn.cursor()
    cur.execute('''
    select slaveuser.name, slave.name from project as slave
    join project_rel on project_rel.slave_id=slave.id
    join project as master on project_rel.master_id=master.id
    join user as slaveuser on slave.user_id=slaveuser.id
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
    join user as slaveuser on slave.user_id=slaveuser.id
    join user as masteruser on master.user_id=masteruser.id
    where slaveuser.name=? and slave.name=?
    ''', (user, project))
    supertasks=[row[0]+'/'+row[1] for row in cur]
    cur.close()
    
    #reports.....

    conn.close()

    return dict( user=user, project=project,
            is_subtask=is_subtask, #files=files,
            subtasks=subtasks, supertasks=supertasks)
  except Exception as e:
    #print('project_data problems...')
    print(e)
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
        select project.name from project
        join user on user.id=project.user_id
        join status on project.status=status.id
        where user.name=? and status.category=0
    ''', (username,))]
    subtasks=[p for p, in cur.execute('''
        select project.name from project
        join user on user.id=project.user_id
        join status on project.status=status.id
        where user.name=? and status.category=1
    ''', (username,))]
    #qa tasks: 
    #find builds w/o test report for all watched projects....
    qatasks=list(cur.execute('''
            with recursive ancestor (project_id) as 
                (select project_id from qa_watch
                join user on user.id=qa_watch.qa_user_id
                where user.name=?
                union select slave_id from project_rel 
                join ancestor on ancestor.project_id=project_rel.master_id)
            select build.name, build.project_id, build.impl_id, build.created from build 
            join ancestor on ancestor.project_id=build.impl_id
            join qa_watch on qa_watch.project_id=build.project_id
            where build.id not in (select build_id from test)
    ''', (username,)))
    #find list of implementations for each of them.....
    qatasks= [[bname]+build_sequence(bproject_id, bimpl_id)
        for bname, bproject_id, bimpl_id, bcreated in qatasks]
    
    reports=()#reports: find all reports for this user's projects....
    
    return dict(user=username, projects=projects, subtasks=subtasks, quatasks=qatasks, reports=reports)
  except Exception as e:
    print(e)
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
            return True
        cur.close()
        conn.close()
    except:
        pass
    return False
    
def email_exists(email):
    try:
        conn=connect(db_name)
        cur=conn.cursor()
        cur.execute('''
        select email from user where email=?
        ''', (email,))
        for row in cur:
            return True
        cur.close()
        conn.close()
    except:
        pass
    return False

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
    
def add_project(user, project):
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
    insert into project (user_id, name, status) 
    select user.id, ?, 0 from user where name=?
    ''', (project, user))
    conn.commit()
    cur.close() 
    conn.close()

def add_impl(user, project, st_user, st):
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
        insert into project (user_id, name, status) 
        select user.id, ?, 6 from user where name=?
        ''', (project, user))
    cur.execute('''
        insert into project_rel (slave_id, master_id)
        select ?, project.id from project
        join user on project.user_id=user.id
        where user.name=? and project.name=?
        ''',(cur.lastrowid, st_user, st))
    conn.commit()
    cur.close() 
    conn.close()

def add_subtask(user, project, st):
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
        insert into project (user_id, name, status) 
        select user.id, ?, 2 from user where name=?
        ''', (st, user))
    cur.execute('''
        insert into project_rel (slave_id, master_id)
        select ?, project.id from project
        join user on project.user_id=user.id
        where user.name=? and project.name=?
        ''',(cur.lastrowid, user, project))
    conn.commit()
    cur.close() 
    conn.close()

def add_test_project(user, project, st):
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
        insert into project (user_id, name, status) 
        select user.id, ?, 1 from user where name=?
        ''', (project, user))
    cur.execute('''
        insert into project_rel (slave_id, master_id)
        select project.id, ? from project
        join user on project.user_id=user.id
        where user.name=? and project.name=?
        ''',(cur.lastrowid, user, st))
    conn.commit()
    cur.close() 
    conn.close()

def clone_project(old_user, old_project, new_user, new_project):
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
        insert into project (user_id, name, status)
        select newuser.id, ?, oldproject.status from project as oldproject
        join user as olduser on olproject.user_id=olduser.id
        join user as newuser
        where newuser.name=? and oldproject.name=? and olduser.name=?
        ''', (new_project, new_user, old_project, old_user))
    new_id=cur.lastrowid
    old_id=list(cur.execute('''
        select project.id from project
        join user on project.user_id=user.id
        where user.name=? and project.name=?
        ''', (old_user, old_project)))
    cur.execute('''
        insert into project_rel (master_id, slave_id)
        select ?, slave_id from project_rel
        where master_id=?
        ''', (new_id, old_id))
    cur.execute('''
        insert into project_rel (master_id, slave_id)
        select master_id, ? from project_rel
        where slave_id=?
        ''', (new_id, old_id))
    build_id=cur.lastrowid
    conn.commit()
    cur.close() 
    conn.close()
    return build_id
    
def add_build(proj_user, project, impl_user, impl):
    conn=connect(db_name)
    cur=conn.cursor()
    cur.execute('''
        insert into build (project_id, impl_id, created)
        select main.id, impl.id, now
        from project as main
        join user as mainuser on main.user_id=mainuser.id
        join project as impl 
        join user as impluser on impl.user_id=impluser.id
        where mainuser.name=? and main.name=?
        and imluser.name=? and impl.name=?
        ''', (proj_user, project, impl_user, impl))
    conn.commit()
    cur.close() 
    conn.close()
    pass#.....

        
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
        cur.close()
        conn.close()
    except:
        pass
    return False

def get_qa_list(user, project):
    "Get all QAs watching this project"
    conn=connect(db_name)
    cur=conn.cursor()
    res=[qa for qa, in cur.execute('''
    select qauser.name from user
    join project on project.user_id=user.id
    join qa_watch on qa_watch.project_id=project.id
    join user as qauser on qa_watch.qa_user_id=qauser.id
    where user.name=? and project.name=?
    ''', (user, project))]   
    cur.close()
    conn.close()
    return res 

def build_sequence(proj_id, impl_id):
    "Sequence of projects (from project to impl, excluding subtasks)"
    conn=connect(db_name)
    cur=conn.cursor()
    res=list(cur.execute('''
    with recursive prj as (
        select id, user.name ||'/'|| project.name as name from project
        join user on project.user_id=user.id
        where id=?
        union select master_id,
            (case when status.category=0 then user.name ||'/'|| project.name ||'+' else '' end)|| prj.name
        from prj
        join project_rel on prj.id=slave_id
        join project on master_id=project.id
        join user on project.user_id=user.id
        join status on project.status=status.id
    ) select name from prj where id=? limit 1
    ''', (impl_id, proj_id)))
    cur.close()
    conn.close()
    return res[0][0].split('+')
    
def get_base(user, project):
    print('get_base', user, project)
    try:
        "Return base subtask's name"
        conn=connect(db_name)
        cur=conn.cursor()
        res=list(cur.execute('''
            select super.name from project as super
            join project_rel on super.id=master_id
            join project on project.id=slave_id
            join user on user.id=project.user_id
            where project.status=6 
            and user.name=? and project.name=?
        ''', (user, project)))
        cur.close()
        conn.close()
        print('base is', res)
        return res[0][0] if res else None
    except Exception as e:
        print(e)
        return None