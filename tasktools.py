#!cmd /k py -3
from vfs import DictVFS
import re

        
class Project(DictVFS):
    #SubdirVFS with additional information.....
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        super().__init__(*args, **kwargs)

def find_fragments(project):
    fragments=[]
    for filename in project.get_all_files():
        print('file:', filename)
        nested=0; ln=0
        for s in project.load(filename):
            ln+=1
            print(ln, ':', s, end='')
            #find ":subtask SUBTASKNAME:" and ":endsubtask:",
            #skip nested fragments:
            stname=re.findall(r':subtask\s([^:\s]+):', s)
            if stname:
                print('subtask:', stname[0])
                if nested==0:
                    fragments+=[dict(
                            begin=ln,
                            name=stname[0],
                            globalname='%s@%s' % (stname[0].split('/', 1)[0], project.id),
                            filename=filename)]
                nested+=1
            elif s.find(':endsubtask:')>=0:
                nested-=1
                if nested==0:
                    fragments[-1]['end']=ln
    return fragments

    
def extract_subtasks(project):
    subtasks={}
    for fr in find_fragments(project):
        if fr['globalname'] not in subtasks:
            subtasks[fr['globalname']]=Project(implements=fr['globalname'])
        
        subtasks[fr['globalname']].save(fr['filename'], 
        subtasks[fr['globalname']].load(fr['filename'])
        +project.load(fr['filename'])[fr['begin']-1:fr['end']])
    return subtasks
    
def apply_subtasks(project, impls):
    for impl in impls:
        #get subtask data and subst it into project.....
        #also copy new files (if they do not already exist in project)....
        pass
    
def text2list(text):
    return list(map(lambda s:s+'\n', text.split('\n')))
    
if __name__=='__main__':
    myproj=Project(
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
        },
        id='0000')
    print(myproj.get_all_files())
    #print(myproj.load('subdir/file'))
    #print(myproj.root)
    print(find_fragments(myproj))
    sts=extract_subtasks(myproj)
    for st in sts:
        print(st)
        print(sts[st].root)