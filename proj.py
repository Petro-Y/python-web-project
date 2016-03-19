# project factory implementation

import vfs
#import db
import tasktools
from settings import usersdir, buildsdir

from uuid import uuid4

def project_by_name(user, project):
    #go to users root dir, create project_vfs object:
    print("I'm project_by_name", user, project)
    path=usersdir+user+'/'+project
    project_vfs=vfs.DiskVFS(path)
    #or extract it from cache(?) ....
    #add properties (stored in db): subtasks, supertasks, status....
    return project_vfs

def project_fork(old_user, old_project, new_user, new_project):
    path=usersdir+old_user+'/'+old_project
    old_project_vfs=vfs.DiskVFS(path)
    path=usersdir+new_user+'/'+new_project
    new_project_vfs=vfs.DiskVFS(path)
    #copy files.....
    #copy some data.......
    pass

def build(user, project, implementations):
    buildname=str(uuid4())#unical random name
    path=buildsdir+buildname
    build_vfs=vfs.DiskVFS(path)
    path=usersdir+user+'/'+project
    project_vfs=vfs.DiskVFS(path)
    #copy project_vfs => build_vfs....
    #apply_subtasks in a temporary copy of the project....
    #store buid info in db....
    return buildname

def integrate(user, project, implementations):
    #apply_subtasks permanently......
    pass

def getzip(user, project):
    pass #generate (or find) zip for project.......

def fromzip(user, project, arch):
    pass #extract files from zip.....