# project factory implementation

import vfs
import db
import tasktools
from settings import usersdir

def project_by_name(user, project):
    #go to users root dir, create project_vfs object:
    path=usersdir+user+'/'+project
    project_vfs=vfs.DiskVFS(path)
    #or extract it from cache(?) ....
    #add properties (stored in db): subtasks, supertasks, status....
    pass

def project_fork(old_user, old_project, new_user, new_project):
    #copy files.....
    #copy some data.......
    pass

def build(user, project, implementations):
    #apply_subtasks in a temporary copy of the project....
    pass

def integrate(user, project, implementations):
    #apply_subtasks permanently......
    pass