import os
path = os.path.abspath(__file__)
rootdir = os.path.dirname(path)+'/'
#rootdir='./'

db_name=rootdir+'project.db'
usersdir=rootdir+'users/'
buildsdir=rootdir+'builds/'

passhashsecret='3f61a0a041fe98decc152b1d5f94ea63'
secret_key='8ffc1cececb0a97ae8d6045dbf75fd49'
