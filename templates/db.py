import sqlite3

def create_db():

    conn=sqlite3.connect('library')
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
            owner_id int);

    ''')
    conn.commit()
    cur.close()
    conn.close()
