import vfs
import re

def find_subtasks(project):
    subtasks=[]
    for filename in project.get_all_files():
        nested=0; ln=0
        for s in project.load(filename):
            ln+=1
            #find ":subtask SUBTASKNAME:" and ":endsubtask:",
            #skip nested subtasks:
            stname=re.findall(r':subtask\s([^:\s]+):', s)
            if stname:
                if nested==0:
                    subtasks+=[lambda:None]
                    subtasks[-1].begin=ln
                    subtasks[-1].name=stname[0]
                    subtasks[-1].filename=filename
                nested+=1
            elif s.find(':endsubtask:')>=0:
                nested-=1
                if nested==0:
                    subtasks[-1].end=ln
    return subtasks
    
def subtask_id(baseproject, st):
    # st.name may be actually a name of a fragment: subtask/fragment......
    #return smth like subtask@baseprojectID.....
    pass
    
def extract_subtasks(project):
    subtasks=find_subtasks(project)
    projects={}
    for st in subtasks:
        if st.name not in projects:
            projects[st.name]=Project(implements=st.name)#use subtask id instead....
        with projects[st.name].open(st.filename, 'a') as f:
            for s in project.load(filename)[st.begin-1:st.end]:
                f.write(s)
    return projects
    
def apply_subtasks(project, impls):
    for impl in impls:
        #get subtask data and subst it into project.....
        #also copy new files (if they do not already exist in project)....
        pass