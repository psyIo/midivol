import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from midivol_win import Midivol

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "MidivolService"
    _svc_display_name_ = "Midivol Service"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
		midivol = Midivol(device=1) #set device ID here
		midivol.start()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)