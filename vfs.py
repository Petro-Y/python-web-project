#!py -3 -i
import re
import os
import os.path

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
    def clone(self, another_vfs):
        #remove all files:
        for f in self.get_all_files():
            self.rm(f)
        #copy all files from another_vfs:
        for f in another_vfs.get_all_files():
            self.save(f, another_vfs.load(f))
        return self
    def get_all_files(self, path=''):
        for fname in map(lambda fname: path+'/'+fname, self.ls(path)):
            if self.isdir(fname):
                yield from self.get_all_files(fname)
            else:
                yield fname
    def get_all_dirs(self): 
        for fname in map(lambda fname: path+'/'+fname, self.ls(path)):
            if self.isdir(fname):
                yield fname
                yield from self.get_all_dirs(fname)
    def mkdir(self, path): pass
    def rm(self, path): pass
    def ls(self, path): pass
    def exists(self, path): pass
    def isdir(self, path): pass
    def load(self, path):  pass
    def save(self, path, linelist): pass

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
        self.lst+=[s+'\n']
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
    def localpath(self, path):
        path=re.sub(r'^[\\/]*', '', path)
        return os.path.join(self.basepath, path)    
    def open(self, path, mode='r', *args, **kwargs):
        path=self.localpath(path)
        if set(mode) & {'w', 'a', 'x'}:
            os.makedirs(os.path.dirname(path))
            #create all directories for this file if they don't exist
        return open(path, mode, *args, **kwargs)
        
    def mkdir(self, path): 
        path=self.localpath(path)
        os.makedirs(path)
        
    def rm(self, path):
        path=self.localpath(path)
        os.remove(path)
        
    def ls(self, path): 
        path=self.localpath(path)
        return os.listdir(path)
        
    def exists(self, path): 
        return os.path.exists(self.localpath(path))
    def isdir(self, path): 
        return os.path.isdir(self.localpath(path))
    #def load(self, path):  pass
    #def save(self, path, linelist): pass        
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

