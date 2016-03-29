# project factory implementation

import vfs
import db
import tasktools
from settings import usersdir, buildsdir

from uuid import uuid4

def project_by_name(user, project=None):
    if project==None:
        return project_by_name(*user.split('/', 1))
    #go to users root dir, create project_vfs object:
    print("I'm project_by_name", user, project)
    path=usersdir+user+'/'+project
    project_vfs=vfs.DiskVFS(path)
    #or extract it from cache(?) ....
    #add properties (stored in db): subtasks, supertasks, status....
    project.base=db.get_base(user, project) 
    return project_vfs

def project_fork(old_user, old_project, new_user, new_project):
    path=usersdir+old_user+'/'+old_project
    old_project_vfs=vfs.DiskVFS(path)
    path=usersdir+new_user+'/'+new_project
    new_project_vfs=vfs.DiskVFS(path)
    #copy some data in db:
    db.clone_project(old_user, old_project, new_user, new_project)
    #copy files:
    new_project_vfs.clone(old_project_vfs)

def build(user, project, implementations):
    buildname=str(uuid4())#unical random name
    path=buildsdir+buildname
    build_vfs=vfs.DiskVFS(path)
    path=usersdir+user+'/'+project
    project_vfs=vfs.DiskVFS(path)
    #copy project_vfs => build_vfs:
    build_vfs.clone(project_vfs)
    #apply_subtasks in a temporary copy of the project
    implementations=proj_sequence(implementations)
    tasktools.apply_subtasks(build_vfs, implementations)
    #store buid info in db....
    return buildname

def integrate(user, project, implementations):
    "apply_subtasks permanently"
    project_vfs=project_by_name(user, project)
    implementations=proj_sequence(implementations)
    tasktools.apply_subtasks(build_vfs, implementations)
    #store information about this build.....
    pass


def proj_sequence(build_seq):
    return list(map(project_by_name, build_seq))

def project_data(user, project):
    return dict(files=project_by_name(user, project).get_all_files(),
        **db.project_data(user, project))

def add_test_project(user, project, st):
    db.add_test_project(user, project, st)
    #create empty directory, or clone master project?....
    
def add_subtask(user, project, st):
    db.add_subtask(user, project, st)
    #extract subtask files from project.....
    
def add_impl(user, project, st_user, st):
    db.add_impl(user, project, st_user, st)
    #clone subtask files:
    st_vfs=project_by_name(st_user, st)
    impl_vfs=project_by_name(user, project)
    impl_vfs.clone(st_vfs)
    
def find_subtasks(user, project):
    subtasks=extract_subtasks(project_by_name(user, project))
    #store them on disk.....
    pass