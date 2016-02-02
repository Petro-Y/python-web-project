#!cmd /k py -3
import vfs
import re

def find_subtasks(project):
    subtasks=[]
    for filename in project.get_all_files():
        print('file:', filename)
        nested=0; ln=0
        for s in project.load(filename):
            ln+=1
            print(ln, ':', s, end='')
            #find ":subtask SUBTASKNAME:" and ":endsubtask:",
            #skip nested subtasks:
            stname=re.findall(r':subtask\s([^:\s]+):', s)
            if stname:
                print('subtask:', stname[0])
                if nested==0:
                    subtasks+=[dict(
                            begin=ln,
                            name=stname[0],
                            globalname='%s@%s' % (stname[0].split('/', 1)[0], project.id),
                            filename=filename)]
                nested+=1
            elif s.find(':endsubtask:')>=0:
                nested-=1
                if nested==0:
                    subtasks[-1]['end']=ln
    return subtasks

    
def extract_subtasks(project):
    subtasks=find_subtasks(project)
    projects={}
    for st in subtasks:
        if st.name not in projects:
            projects[st.name]=Project(implements=st.name)#use subtask id instead....
        # with projects[st.name].open(st.filename, 'a') as f:
            # for s in project.load(filename)[st.begin-1:st.end]:
                # f.write(s)
        prjects[st.name].save(st.filename, projects[st.name].load(st.filename)+project.load(filename)[st.begin-1:st.end])
    return projects
    
def apply_subtasks(project, impls):
    for impl in impls:
        #get subtask data and subst it into project.....
        #also copy new files (if they do not already exist in project)....
        pass
    
def text2list(text):
    return list(map(lambda s:s+'\n', text.split('\n')))
    
if __name__=='__main__':
    myproj=vfs.DictVFS(
        {
            'file':text2list('''
                    #include <stdio.h>
                    main()
                        {
                        /* :subtask one: */
                        // write some instructions here
                        /* :endsubtask: */
                        }
                    '''),
            'subdir':{
                'file': text2list('''
                        Hi!!!
                        :subtask two:
                        some text here
                        :endsubtask:
                        lorem ipsum dolor...
                        :subtask two/2:
                        another text here
                        :endsubtask:
            ''')}
        })
    myproj.id='0000'
    print(myproj.get_all_files())
    #print(myproj.load('subdir/file'))
    #print(myproj.root)
    print(find_subtasks(myproj))