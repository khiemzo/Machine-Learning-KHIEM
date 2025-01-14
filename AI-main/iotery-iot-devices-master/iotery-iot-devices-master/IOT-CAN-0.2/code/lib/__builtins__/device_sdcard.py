#-----------------------
# notify
#-----------------------

print('LOAD: system_sdcard.py')

#-----------------------
# imports
#-----------------------

import os,sys,time
from machine import SDCard

import system_tools as st

#-----------------------
# tools class
#-----------------------

class SDCARD:

    mount_point = '/sd' # target mount point
    
    _sdcard = None # SDCard object
    _mount_point = None # current mount point
    _slot = 2 # using spi slot 2 (cs=5,sck=18,miso=19,mosi=23)    

    def error(self,e=None,s='SDCard not mounted.',unmount=False):

        if e:
            sys.print_exception(e)

        if s:
            print('ERROR:',s)

        if unmount:
            print('SDCard MAJOR ERROR! Unmounting.')
            self.unmount(show=True)

    def sdpath(self,path=None):

        if not (self._sdcard and self._mount_point):
            self.error()
            return None

        path = path or ''
        path = [x.replace(' ','') for x in path.split('/') if x.replace(' ','')]

        if path:
            return self._mount_point + '/' + '/'.join(path)

        return self._mount_point

    def mount(self):

        self.unmount(show=False)

        try:
            self._sdcard = SDCard(slot=self._slot)
            self.mount_point = self.mount_point.replace(' ','').rstrip('/')
            self.mount_point = self.mount_point or '/sd'
            os.mount(self._sdcard,self.mount_point)
            self._mount_point = self.mount_point
            time.sleep_ms(100)
            print('SDCard mount at',self._mount_point)
            return True

        except Exception as e:
            self.error(e,'SDCard mount failed.')
            self.unmount(show=False)
            return False

    def unmount(self,show=True):

        try:
            os.umount(self._mount_point)
            self._mount_point = None

            self._sdcard.deinit()
            self._sdcard = None

            if show:
                print('SDCard unmounted.')
            return True

        except Exception as e:
            if show:
                self.error(e,'SDCard stage 1 unmount failed.')
        
            try:
                self._sdcard.deinit()

                if show:
                    print('SDCard stage 2 deinit success.')

            except Exception as e:
                if show:
                    self.error(e,'SDCard stage 2 deinit failed.')

        self._mount_point = None
        self._sdcard = None

        return False

    def format(self,warn=True):

        if warn:
            print()
            print('WARNING: This will DESTROY ALL DATA on the SDCard!!!')
            print()
            print('Are you sure you want to continue?',end=' ')
            if (input('> ').strip()+'n')[0].lower() != 'y':
                return False

        try:

            self.unmount(show=False)

            _sdcard = SDCard(slot=self._slot)
            os.VfsFat.mkfs(_sdcard)
            _sdcard.deinit()
            print('SDCard Fat32 format complete.')

            self.mount()
            with self.open('FAT32_FORMAT','w') as f:
                f.write(str(time.time())+'\n')
                f.close()
            print('SDCard initial write success.')

            return True

        except Exception as e:
            self.error(e,'SDCard format failed.')

    def tree(self,d=None):

        d = self.sdpath(d)

        if d:
            try:
                st.tree(d)

            except Exception as e:
                self.error(e,unmount=True)

        else:
            return None

    def mkdir(self,d):

        d = self.sdpath(d)

        if d and d != self._mount_point:
            try:
                return st.mkdir(d)

            except Exception as e:
                self.error(e,unmount=True)

        return False

    def rmdir(self,d):

        d = self.sdpath(d)

        if d and d != self._mount_point:
            try:
                return st.rmdir(d)

            except Exception as e:
                self.error(e,unmount=True)

        return False

    def remove(self,f):

        f = self.sdpath(f)

        if f:
            try:
                if st.isfile(f):
                    return st.rmdir(f)
                return False

            except Exception as e:
                self.error(e,unmount=True)

        return False

    def isfile(self,f):

        f = self.sdpath(f)

        if f:
            try:
                return st.isfile(f)

            except Exception as e:
                self.error(e,unmount=True)

        return False

    def isdir(self,d):
        
        d = self.sdpath(d)

        if d:
            try:
                return st.isdir(d)

            except Exception as e:
                self.error(e,unmount=True)

        return False

    def exists(self,fd):

        fd = self.sdpath(fd)

        if fd:
            try:
                return st.exists(fd)

            except Exception as e:
                self.error(e,unmount=True)

        return False

    def pf(self,f):

        f = self.sdpath(f)

        if f:
            try:
                if st.isfile(f):
                    st.pf(f)

            except Exception as e:
                self.error(e,unmount=True)

    def open(self,f,mode='r',encoding='utf8'):

        f = self.sdpath(f)

        if f:
            try:
                return open(f,mode=mode,encoding=encoding)

            except Exception as e:
                self.error(e,unmount=True)

        return None

#-----------------------
# end
#-----------------------
