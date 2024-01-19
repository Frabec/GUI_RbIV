import queue
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class Watchdog_runs(Observer, FileSystemEventHandler):
    def __init__(self, path, backend, type):
        self.path=path
        self.backend=backend
        FileSystemEventHandler.__init__(self)
        Observer.__init__(self)
        self.schedule(self, recursive=False, path=self.path)
        self.start()
        self.last_created_path=None
        self.type=type #if type is 0 we monitor runs, if type is 1 we monitor images

    # def on_any_event(self, event):
    #     print(event)
    def on_created(self, event):
        if not self.is_alive():
            return
        if event.is_directory:
            if self.last_created_path is None:
                # time.sleep(1.5) #Wait until Camera program has time to save the 3 pictures, if we don't wait the program crashes
                self.backend.notify_runs(event, self.type)
                self.last_created_path=event.src_path
            else: 
                if event.src_path==self.last_created_path:
                    return
                else: 
                    # time.sleep(1.5) #Wait until Camera program has time to save the 3 pictures, if we don't wait the program crashes
                    self.backend.notify_runs(event, self.type)
                    self.last_created_path=event.src_path

    # def on_modified(self, event):
    #     print(event)
    #     if event.is_directory:
    #         self.backend.notify_runs(event)
    def on_deleted(self, event):
        if not self.is_alive():
            return
        #Check that indeed the file doesn't exist anymore
        if not os.path.exists(event.src_path):
            self.backend.notify_runs(event, self.type)
    def kill(self):
        self.stop()
        self.join(timeout=2)
        if self.is_alive():
            print("Impossible to join thread")
            # raise Exception("Impossible to join thread")
        else: 
            print("Thread joined")

class Backend:
    MONITOR_RUNS=0
    MONITOR_IMAGES=1
    def __init__(self, ui_root):
        self.ui_root=ui_root
        #Queue for run watchdog events
        self.runs_queue=queue.Queue()
        self.watchdog_runs=None
        self.images_queue=queue.Queue()
        self.watchdog_images=None
    

    def start_run_watchdog(self, path):
        self.watchdog_runs=Watchdog_runs(path, self, self.MONITOR_RUNS)

    def start_images_watchdog(self, path, run):
        run_path= os.path.join(path, run)
        self.watchdog_images=Watchdog_runs(run_path, self, self.MONITOR_IMAGES)

    def stop_images_watchdog(self):
        if self.watchdog_images is not None : 
            #If we were watching another run we terminate this run
            self.watchdog_images.kill()
            #We empty the queue
            with self.images_queue.mutex:
                self.images_queue.queue.clear()

    def stop_runs_watchdog(self):
        if self.watchdog_images is not None : 
            #If we were watching another run we terminate this run
            self.watchdog_images.kill()
            #We empty the queue
            with self.images_queue.mutex:
                self.images_queue.queue.clear()
    def notify_runs(self, event, type):
        if type == self.MONITOR_RUNS:
            self.runs_queue.put(event)
            self.ui_root.event_generate("<<RunsEvent>>", when="tail")
        if type == self.MONITOR_IMAGES:
            self.images_queue.put(event)
            self.ui_root.event_generate("<<ImagesEvent>>", when="tail")