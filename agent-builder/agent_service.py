import win32serviceutil, win32service, win32event, servicemanager
from agent_core import main_loop

class AtlasPatchService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'AtlasPatch'
    _svc_display_name_ = 'AtlasPatch Agent Service'
    _svc_description_ = 'Collecte télémétrie et applique des mises à jour via AtlasPatch.'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        main_loop()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPED, (self._svc_name_, ''))

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AtlasPatchService)