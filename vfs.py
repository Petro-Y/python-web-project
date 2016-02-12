import re


class VFS:
    '''
    abstract base class for virtual file systems (implemented on real disk file system, 
    memory storage, database etc.''' 
    def translate_path(self, path):
        #add final / ....
        #replace /DIR/../ => /, /./ => /, //=>/ .....
        #remove final / .......
        #add initial / ......
        #ensure path doesn't start from /.. .......
        return path
    def parse_path(self, path):
        return list(filter(lambda s:s, path.split('/')))#also remove empty items
    def get_all_files(self): pass
    def get_all_dirs(self): pass
    def mkdir(self, path): pass
    def rm(self, path): pass
    def ls(self, path): pass
    def exists(self, path): pass
    def isdir(self, path): pass

class ListReadStream:
    def __init__(self, lst):
        self.it=iter(lst)
        
    def __exit__(self):pass
    def read(self):
        try:
            return next(self.it)
        except Exception:
            return ''


class ListWriteStream:
    def __init__(self, lst):
        self.lst=lst
        
    def __exit__(self):pass
    def write(self, s):
        lst+=[s+'\n']
    pass
    
class ListVFS(VFS):
    '''Abstract file system where file can be loaded and saved as a list of strings'''
    def open(self, path, mode='r'): 
        if mode=='r':
            #create iterator with read() and close() metods:
            return ListReadStream(self.load(path))
            
        elif mode=='w':
            #create object with write() method to store data in a list and close() to save the list....
            pass
        elif mode=='a':
            old=self.load(path)
            f=self.open(path, 'w')
            for s in old:
                f.write(s)
            return f
    
class StreamVFS(VFS):
    '''Abstract file system with stream access to file content'''
    def load(self, path): 
        with self.open(path) as f:
            return list(f)
    def save(self, path, linelist): 
        with self.open(path, 'w') as f:
            for s in linelist:
                f.write(s)
    
    
class DiskVFS(StreamVFS):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.basepath=path
        #if such dir not exist, create it....
    pass

class SubdirVFS(VFS):
    #based on subdir of another VFS.....
    def __init__(self, vfs, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.basepath=path
        self.basevfs=vfs
        #if such dir not exist, create it....
    pass

class MergeVFS(VFS):
    '''Join multiple VFSes into single one'''
    def __init__(self, *vfses, **kwargs):
        super().__init__(**kwargs)
        self.vfses=vfses
    pass

class DictVFS(ListVFS):
    #dictionary-based memory VFS.......
    def __init__(self, root=None, **kwargs):
        self.root=root or {}
    def load(self, path):
        try:
            f=self.root
            for name in self.parse_path(path):
                f=f[name]
            return f[:]
        except Exception:
            return []
    def save(self, path, content):
        f=self.root
        names=self.parse_path(path)
        for name in names[:-1]:
            if name not in f:
                f[name]={}
            f=f[name]
        f[names[-1]]=content
    def mkdir(self, path):
        f=self.root
        names=self.parse_path(path)
        for name in names:
            if name not in f:
                f[name]={}
            f=f[name]
    def get_all_files(self, root=None):
        res=[]
        if root==None:
            root=self.root
        for name in root:
            if isinstance(root[name], dict):
                res+=map(lambda s:name+'/'+s, self.get_all_files(root[name]))
            else:
                res+=[name]
        return res
        
class MemVFS(ListVFS):
    #not ready and possibly will be removed. Please dont read this trash :-|
    def __init__(self, *args, **kwargs):
        self.allfiles={}
        self.dirs=[]
   
    def __getitem__(self, path):
        return self.allfiles[translate_path(path)]
        
    def __setitem__(self, path, content):
        self.allfiles[translate_path(path)]=content
        
    def get_all_files(self):
        return self.allfiles
        
    def get_all_dirs(self):
        res=self.dirs.copy()
        res+=map(lambda s: re.sub('/[^/]*$', '', s), self.allfiles)
        #also add superdirs for each dir.....
        return res
