import servicemanager
import socket
import sys
import win32event
import win32service
import win32serviceutil
from datetime import datetime

class TestService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TestService" #Service Name (exe)
    _svc_display_name_ = "Test Service" #Service Name which will display in the Winfows Services Window 
    _svc_description_ = "My service description" ##Service Name which will display in the Winfows Services Window

    def __init__(self, args):
        '''
        Used to initialize the service utility. 
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        '''
        Used to stop the service utility (restart / timeout / shutdown)
        '''
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Used to execute all the piece of code that you want service to perform.
        '''
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            with open('C:\\TestService.log', 'a') as f:
                f.write(f"[TIME={datetime.now()}] test service running...\n")
            rc = win32event.WaitForSingleObject(self.hWaitStop, 100)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TestService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(TestService)
