#-----------------------
# notify
#-----------------------

print('LOAD: system_tools.py')

#-----------------------
# imports
#-----------------------

import os,sys,gc

#-----------------------
# file system tools
#-----------------------

# oct(os.stat(file)[0]) = '0o100000' = file
# oct(os.stat(file)[0]) = '0o40000'  = dir

def abspath(fd=None):

    if not fd:
        return os.getcwd()

    fd = fd.replace(' ','')

    if not fd:
        return os.getcwd()

    if fd == '/':
        return '/'

    if fd[0] == '/':
        return fd.rstrip('/')

    cwd = [x.strip() for x in os.getcwd().split('/') if x.strip()]
    fdl = [x.strip() for x in fd.split('/') if x.strip()]

    if fdl[:len(cwd)] == cwd:
        return '/' + '/'.join(fdl)

    return '/' + '/'.join(cwd+fdl)

def isfile(f):
    try:
        stats = os.stat(f)
        if oct(stats[0])[-5] != '4':
            return True
        else:
            return False
    except:
        return False

def isdir(d):
    try:
        stats = os.stat(d)
        if oct(stats[0])[-5] == '4':
            return True
        else:
            return False
    except:
        return False

def exists(fd):
    try:
        stats = os.stat(fd)
        return True
    except:
        return False

def tree(d=None,i=0):
    
    d = abspath(d)

    if not exists(d):
        print('ERROR: Does not esist:',d)
        return None

    if i:
        print('{}|-/{}'.format('  '*i,d.split('/')[-1]))
    else:
        print(  '  /{}'.format(d.split('/')[-1]))

    listing = os.listdir(d)
    listing.sort()

    dirs = []

    for x in listing:
        x2 = d.rstrip('/')+'/'+x
        stats = os.stat(x2)
        if oct(stats[0])[-5] == '4':
            dirs.append(x2)
        else:
            print('{}|--{} {}'.format('  '*(i+1),x,stats[6]))

    for x2 in dirs:
        tree(x2,i+1)

    if i == 0:
        print(end='  ')
        du()

def mkdir(d):

    d = abspath(d)

    if (not d) or d == '/':
        return False

    if exists(d):
        return False

    dlist = [x.strip() for x in d.split('/') if x.strip()]

    if dlist:

        for x in range(len(dlist)):
            d = '/' + '/'.join(dlist[:x+1])
            if not exists(d):
                try:
                    os.mkdir(d)
                except Exception as e:
                    sys.print_exception(e)
                    print('ERROR: Unable to mkdir():',d)
                    return False

    return True

def remove(f):

    if isfile(f):
        return rmdir(f) # returns True

    elif '*' in f:
        if '/' in f:
            path,f2 = f.rsplit('/',1)
        else:
            path,f2 = '',f
        rc = 0
        if isdir(path) and (f2.startswith('*') or f2.endswith('*')):
            fl = os.listdir(path)
            for f3 in fl:
                if f2.startswith('*') and f3.endswith(f2[1:]):
                    if rmdir(path+'/'+f3):
                        rc += 1
                elif f3.startswith(f2[:-1]):
                    if rmdir(path+'/'+f3):
                        rc += 1
        if rc:
            return True

    return False

def rmdir(d,root=False):

    d = abspath(d)

    if (not d) or (d == '/' and not root):
        return False

    stats = os.stat(d)
    rvalue = True

    try:

        # file
        if oct(stats[0])[-5] != '4':
            print('REMOVE:',d[-48:],end=' ')
            os.remove(d)
            print('DONE')

        # dir
        else:

            cwd = d == os.getcwd()

            for x in os.listdir(d):
                if not rmdir(d.rstrip('/')+'/'+x):
                    rvalue = False

            if not cwd:
                print('RMDIR:',d[-48:],end=' ')
                os.rmdir(d)
                print('DONE')

    except Exception as e:
        print('ERROR')
        rvalue = False

    return rvalue

def pf(f):
    return printfile(f)

def printfile(f):

    if not isfile(f):
        print('FILE:',abspath(f),'Does not exist.')

    else:
        try:
            lc = 0
            with open(f) as openfile:
                for line in openfile:
                    lc += 1
                    print('{:>4}:'.format(lc),line.rstrip())
                openfile.close()
            print('FILE:',abspath(f))
            
        except:
            print('ERROR FILE:',abspath(f))

#-----------------------
# object display
#-----------------------

# pretty print (returns nothing, smaller memory)
def pp(obj,depth=0,indentline=True,newline=True,end='\n'):

    # characters
    ic = ' '
    tab = 4
    
    # string to print
    line = ''

    # start line with indent
    if indentline:
        line += ic*depth

    # list or tuple
    if type(obj) in (list,tuple):
        if type(obj) == list:
            line += '['
            close = ']'
        else:
            line += '('
            close = ')'
        if not obj:
            line += close
            print(line,end=end)
        else:
            print(line)
            for item in obj[:-1]:
                pp(item,depth+1,True,False,end=',\n')
            pp(obj[-1],depth+1,True,False,end='\n')
            print(ic*(depth)+close,end=end)

    # dict
    elif type(obj) == dict:
        line += '{'
        if not obj:
            line += '}'
            print(line,end=end)
        else:
            print(line)
            keys = list(obj.keys())
            keys.sort()
            for key in keys[:-1]:
                pp(key,depth+1,True,False,end=':')
                if type(obj[key]) in (dict,list,tuple):
                    print()
                    pp(obj[key],depth+tab,True,False,end=',\n')
                else:
                    print(end=' ')
                    pp(obj[key],0,False,False,end=',\n')
            key = keys[-1]
            pp(key,depth+1,True,False,end=':')
            if type(obj[keys[-1]]) in (dict,list,tuple):
                print()
                pp(obj[key],depth+tab,True,False,end='\n')
            else:
                print(end=' ')
                pp(obj[key],0,False,False,end='\n')

            print(ic*(depth)+'}',end=end)

    # non-object
    else:
        print(line+repr(obj),end=end)

# pretty string (doesn't print)
def ps(obj,depth=0,indentline=True,newline=True,jsonify=False):

    # this is rudimentary

    # characters
    ns = '\r\n'
    ic = ' '
    tab = 2
    
    # return string
    r = ''

    # start line with indent
    if indentline:
        r += ic*depth

    # list or tuple
    if type(obj) in (list,tuple):
        if type(obj) == list or jsonify:
            r += '['
            close = ']'
        else:
            r += '('
            close = ')'
        if not obj:
            r += close
        else:
            r += ns
            for item in obj[:-1]:
                r += ps(item,depth+tab,True,False,jsonify)
                r += ',' + ns
            r += ps(obj[-1],depth+tab,True,False,jsonify)
            r += ns
            r += ic*(depth) + close

    # dict
    elif type(obj) == dict:
        r += '{'
        if not obj:
            r += '}'
        else:
            r += ns
            keys = list(obj.keys())
            keys.sort()
            for key in keys[:-1]:
                r += ps(key,depth+tab,True,False,jsonify='string')
                r += ':'
                if type(obj[key]) in (dict,list,tuple):
                    r += ns + ps(obj[key],depth+tab+tab,True,False,jsonify)
                else:
                    r += ' ' + ps(obj[key],0,False,False,jsonify)
                r += ',' + ns
            r += ps(keys[-1],depth+tab,True,False,jsonify)
            r += ':'
            if type(obj[keys[-1]]) in (dict,list,tuple):
                r += ns + ps(obj[keys[-1]],depth+tab+tab,True,False,jsonify)
            else:
                r += ' ' + ps(obj[keys[-1]],0,False,False,jsonify)
            r += ns
            r += ic*(depth) + '}'

    # json non-objects
    elif jsonify:
        if jsonify == 'string':
            obj = str(obj)
        if obj == None:
            r += 'null'
        elif obj == True:
            r += 'true'
        elif obj == False:
            r += 'false'
        elif type(obj) == str:
            r += '"{}"'.format(obj.replace('\\','\\\\').replace('"','\\"'))
        elif type(obj) in (int,float) and jsonify == 'string':
            r += repr(str(obj))            
        else:
            r += repr(obj)
    
    # non-object
    else:
        r += repr(obj)

    # end with newline
    if newline:
        r += ns    

    # return string
    return r

#-----------------------
# resources
#-----------------------

def reload(module):
    modname = module.__name__
    del sys.modules[modname]
    gc.collect()
    __import__(modname)
    gc.collect()

def du(d=None,h='MB',show=True,rt=False):
    if not d:
        d = os.getcwd()
    for hv,hn in ((1000000000,'GB'),(1000000,'MB'),(1000,'KB'),(1,'B'),(1000000,'MB')):
        if h == hv or h == hn:
            break
    bsize,frsize,blocks,bfree,bavail,files,ffree,favail,flag,namemax = os.statvfs(d)
    size = bsize * blocks
    free = bsize * bfree
    used = size - free
    percent = int(round(100*used/size,2))
    if show:
        print('DISK {}: {:.2f}% of {:.2f}{}'.format(d,percent,size/hv,hn))
    if rt:
        return percent,size

def memp(show=True,collect=True,rt=False):
    if collect:
        gc.collect()
    free  = gc.mem_free()
    alloc = gc.mem_alloc()
    size = free+alloc
    percent = round(100*alloc/size,2)
    if show:
        print('MEMORY: {:.2f}% of {:.2f}KB'.format(percent,size/1000))
    if rt:
        return percent,size

#-----------------------
# end
#-----------------------
