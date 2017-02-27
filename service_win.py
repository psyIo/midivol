import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
from midivol_win import Midivol

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "MidivolService"
    _svc_display_name_ = "Midivol Service"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.midivol.stop_listening = True
        self.midivol.listening_input.close()
        self.midivol.inputs.quit()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.main()

    def main(self):
        device_name = 'Launch Control'
        self.midivol = Midivol(device=1) #set device ID here		
        if self.midivol.assign_device_by_name(device_name):
            self.midivol.build()
            self.log_msg_service(servicemanager.PYS_SERVICE_STARTED, 'running using device "{}"'.format(device_name))      
            while True:
                if self.midivol.stop_listening:
                    break
                if self.midivol.listening_input.poll():
                    msg = self.midivol.listening_input.read(1)
                    self.midivol.set_volume_from_midi_msg(msg)
                    if self.midivol.verbose:	
                        self.log_msg_service(servicemanager.PYS_SERVICE_STARTED,'{} {}'.format(self.midivol.tag, str(msg)))
                        # self.log_msg(msg)
                time.sleep(0.005)	
        else:
            self.log_msg_service(servicemanager.PYS_SERVICE_STOPPED,'{} device was not found'.format(device_name))
            self.SvcStop()			
            
    def log_msg_service(self, event_id, msg, error_type=servicemanager.EVENTLOG_INFORMATION_TYPE):
        servicemanager.LogMsg(error_type, event_id, (self._svc_name_, ', ' + msg))

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)