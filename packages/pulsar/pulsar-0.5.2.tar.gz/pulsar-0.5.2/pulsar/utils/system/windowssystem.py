import sys
import signal
import ctypes
import ctypes.wintypes
import errno
import socket
import getpass
from time import sleep

from pulsar.utils.sockets import socket_pair

from .winprocess import WINEXE
from .base import *

__all__ = ['IOpoll',
           'close_on_exec',
           'Waker',
           'daemonize',
           'EXIT_SIGNALS',
           'get_uid',
           'get_gid',
           'get_maxfd']

# See: http://msdn.microsoft.com/en-us/library/ms724935(VS.85).aspx
SetHandleInformation = ctypes.windll.kernel32.SetHandleInformation
SetHandleInformation.argtypes = (ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD,\
                                 ctypes.wintypes.DWORD)
SetHandleInformation.restype = ctypes.wintypes.BOOL

HANDLE_FLAG_INHERIT = 0x00000001

# The BREAK signal for windows
EXIT_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGABRT, signal.SIGBREAK)
if sys.version_info >= (2, 7):
    SIG_NAMES[signal.CTRL_C_EVENT] = 'CTRL C EVENT'
    EXIT_SIGNALS += (signal.CTRL_C_EVENT,)
    
    
def get_parent_id():
    if ispy32:
        return os.getppid()
    else:
        return None

def chown(path, uid, gid):
    pass

def close_on_exec(fd):
    if fd:
        success = SetHandleInformation(fd, HANDLE_FLAG_INHERIT, 0)
        if not success:
            raise ctypes.GetLastError()
        
def _set_non_blocking(fd):
    pass

def get_uid(user=None):
    if not user:
        return getpass.getuser()
    elif user == getpass.getuser():
        return user

def get_gid(group=None):
    return None

def setpgrp():
    pass

def get_maxfd():
    return MAXFD

def daemonize():
    pass


class IOpoll(IOselect):
    '''The default windows IO poll class. Based on select.'''
    def poll(self, timeout=None):
        """Win32 select wrapper."""
        if not (self.read_fds or self.write_fds):
            # windows select() exits immediately when no sockets
            if timeout is None:
                timeout = 0.01
            else:
                timeout = min(timeout, 0.001)
            sleep(timeout)
            return ()
        # windows doesn't process 'signals' inside select(), so we set a max
        # time or ctrl-c will never be recognized
        if timeout is None or timeout > 0.5:
            timeout = 0.5
        return super(IOpoll, self).poll(timeout)
    
    
class Waker(object):
    '''In windows'''
    def __init__(self):
        self._writer, s = socket_pair(backlog=1)
        s.setblocking(True)   
        self._reader, addr = s.accept()
        self._writer.setblocking(False)
        self._reader.setblocking(False)
        s.close()
        
    def __str__(self):
        return 'Socket waker {0}'.format(self.fileno())
        
    def fileno(self):
        return self._reader.fileno()
    
    def wake(self):
        try:
            self._writer.send(b'x')
        except IOError:
            pass
        
    def consume(self):
        try:
            result = True
            while result:
                result = self._reader.recv(1024)
        except IOError:
            pass

    def close(self):
        self.reader.close()
        self.writer.close()
        
