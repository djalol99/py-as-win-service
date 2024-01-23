import servicemanager
import socket
import sys
import win32event
import win32service
import win32serviceutil

from scale_ws_app import get_ws_server


# <<< Windows Service
class BaseService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WeightScale" #Service Name (exe)
    _svc_display_name_ = "Weight Scale Data Reader" #Service Name which will display in the Winfows Services Window 
    _svc_description_ = "Reading data throug serial ports" #Service Name which will display in the Winfows Services Window

    def __init__(self, *args):
        '''
        Used to initialize the service utility. 
        '''
        super().__init__(*args)
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
        ws_server = get_ws_server(port=7001)
        while rc != win32event.WAIT_OBJECT_0:
            ws_server.handle_request()
            rc = win32event.WaitForSingleObject(self.hWaitStop, 100)
        ws_server.close()

    @classmethod
    def run(cls, args: list):
        if len(args) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(cls)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(cls)    
# >>> Windows Service


if __name__ == "__main__":
    BaseService.run(sys.argv)
