import elog as _elog_ha
from getpass import getuser as _getuser
from getpass import getpass as _getpass
import os, datetime

def getDefaultElogInstance(url,**kwargs):
    from pathlib import Path
    home = str(Path.home())
    if not ('user' in kwargs.keys()):
        kwargs.update(dict(user=_getuser()))

    if not ('password' in kwargs.keys()):
        try:
            with open(os.path.join(home,'.elog_psi'),'r') as f:
                _pw = f.read().strip()
        except:
            print('Enter elog password for user: %s'%kwargs['user'])
            _pw = _getpass()
        kwargs.update(dict(password=_pw))

    return _elog_ha.open(url,**kwargs),kwargs['user']

class Elog:
    def __init__(self,url,screenshot_directory='',**kwargs):
        self._log,self.user = getDefaultElogInstance(url,**kwargs)
        self._screenshot_directory = screenshot_directory
        self.read = self._log.read

    def post(self,*args,**kwargs):
        """
        """
        if not ('Author' in kwargs):
            kwargs['Author'] = self.user
        return self._log.post(*args,**kwargs)

    def screenshot(self,message='', window=False, desktop=False, delay=3, **kwargs):
        cmd = ['gnome-screenshot']
        if window:
            cmd.append('-w')
            cmd.append('--delay=%f'%delay)
        elif desktop:
            cmd.append('--delay=%f'%delay)
        else:
            cmd.append('-a')
        tim = datetime.datetime.now()
        fina = '%s-%s-%s_%s-%s-%s'%tim.timetuple()[:6]
        if 'Author' in kwargs.keys():
            fina+='_%s'%user
        else:
            fina+='_%s'%self.user
        fina+='.png'
        filepath = os.path.join(self._screenshot_directory,fina)
        cmd.append('--file=\"%s\"'%filepath)
        os.system(' '.join(cmd))
        
        kwargs.update({'attachments':[filepath]})
        self.post(message,**kwargs)








        



