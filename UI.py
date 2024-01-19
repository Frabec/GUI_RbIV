#!/usr/bin/python
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import configparser
import tkinter as tk 
from scipy.constants import c
import matplotlib


# matplotlib.use('TkAgg')
import scipy.constants as c
# from backend_tkagg2 import FigureCanvasTkAgg, NavigationToolbar2Tk

from matplotlib.figure import Figure
import tkinter as tk
from tkinter.messagebox import askyesno
import datetime
#local imports
from backend import Backend
import folder_explorer
from frames import FileFrame, PlotFrame, give_focus
import config
import analysis
import sys
import time

class MainApplication(tk.Frame, folder_explorer.FolderExplorer):
    def __init__(self, parent, day=None,*args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.backend=Backend(parent)
        ## Variables ##
        self.day=day
        if self.day is None:
            self.day_path = self.find_last_day(config.config_parser["filesystem"]["passerelle_path"]) #finds the path to last day where images where recorded
            print(self.day_path)
        else :
            day_new=day.strftime("%d%b%Y")
            year=day_new[5:]
            month=day_new[2:5]+year
            browse_day=day_new[5:]+month
            print(config.config_parser["filesystem"]["passerelle_path"] +year+os.path.sep+month+os.path.sep+day_new+os.path.sep+'Pictures'+os.path.sep+'RAW')
            #self.day_path = config.config_parser["filesystem"]["passerelle_path"] +os.path.sep+self.day.__str__().replace("-", os.path.sep)
            self.day_path=config.config_parser["filesystem"]["passerelle_path"] +year+os.path.sep+month+os.path.sep+day_new+os.path.sep+'Pictures'+os.path.sep+'RAW'
        ## Frames ##
        self.fileFrame=FileFrame(self.parent,self)
        self.fileFrame.grid(column= 1, row=2)
        self.plotFrame= PlotFrame(self.parent,self)
        self.plotFrame.grid(row=1, column=1)
        self.parent.bind("<<RunsEvent>>", self.handle_runs_event)
        self.parent.bind("<<ImagesEvent>>", self.handle_images_event)
        self.parent.bind("<<CursorEvent>>", self.on_new_cursor)
        self.analysis=None

        ##############################################
        self.start()

    #Callbacks

    def start(self):
        #Initial runs
        self.init_runs()
        #Start watchdog on folders
        self.backend.start_run_watchdog(self.day_path)
    
    #handles events triggered when a run is deleted or created
    def handle_runs_event(self, event):
        new_event=self.backend.runs_queue.get()
        print('new_event {} '.format(new_event))
        if new_event.event_type=="created":
            self.add_new_run(new_event.src_path)
        elif new_event.event_type=="deleted":
            self.delete_run(new_event.src_path)
        else:
            print("Unknown run event type")
    
    #handles events triggered when an image is deleted or created
    def handle_images_event(self, event):
        new_event=self.backend.images_queue.get()
        selection=self.fileFrame.list_images.curselection() #image before modifying the list
        if not selection: #We check if an image is selected before adding or removing an image
            is_selection=False
        else:
            is_selection=True
            before_change=self.fileFrame.list_images.get(self.fileFrame.list_images.curselection()[0])
        if new_event.event_type=='created':
            self.add_new_image(new_event.src_path)#We add the new image to the list
            live_update=self.fileFrame.var_live_update.get() 
            if live_update: #If we want to live update we have to switch the selection to the most recent image
                self.fileFrame.list_images.select_clear(0,'end')
                self.fileFrame.list_images.selection_set(0) #we put the selection back on the first element
        elif new_event.event_type=='deleted':
            self.delete_image(new_event.src_path)
        
        else : 
            print("Unknown image event type")
        index_after_change=self.fileFrame.list_images.curselection()[0]
        after_change=self.fileFrame.list_images.get(index_after_change)
        if is_selection and before_change != after_change: #If selection changed we reanalyze the result
            self.analyze_image(after_change)


    def on_new_image_selected(self, event):
        self.analyze_image(self.fileFrame.list_images.get(self.fileFrame.list_images.curselection()[0]))


    def on_new_run_selected(self, event):
        index_new_run=self.fileFrame.list_runs.curselection()[0]
        new_run=self.fileFrame.list_runs.get(index_new_run)
        start_time=time.time()
        self.backend.stop_images_watchdog() #we stop the previous watch on previous run dir
        print(f"Time to stop watchdog: {time.time()-start_time:} s")
        start_time=time.time()
        self.init_images() #we initialize the images
        print(f"Time to init images: {time.time()-start_time:} s")
        self.fileFrame.list_images.selection_clear(0,'end')
        self.fileFrame.list_images.selection_set(0)
        start_time=time.time()
        self.analyze_image(self.fileFrame.list_images.get(0))
        print(f"Time to analyze first image: {time.time()-start_time:} s")
        start_time=time.time()
        self.backend.start_images_watchdog(self.day_path, new_run) #we start watching the new run dir
        print(f"Time to start watchdog: {time.time()-start_time:} s")
    
    #Put name of selected image in clipboard when right click
    def copy_image_selection(self, event):
        index_image_name=self.fileFrame.list_images.curselection()[0]
        image_name=self.fileFrame.list_images.get(index_image_name)
        print(image_name)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(image_name)

    #Put name of selected run in clipboard when right click
    def copy_run_selection(self, event):
        index_image_name=self.fileFrame.list_runs.curselection()[0]
        image_name=self.fileFrame.list_runs.get(index_image_name)
        print(image_name)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(image_name)

    def on_set_view_as_ROI(self):
        xlims, ylims=self.plotFrame.image_plot.get_lims()
        self.plotFrame.var_xmin.set(int(min(xlims[0],xlims[1])))
        self.plotFrame.var_xmax.set(int(max(xlims[0],xlims[1])))
        self.plotFrame.var_ymin.set(int(min(ylims[0],ylims[1])))
        self.plotFrame.var_ymax.set(int(max(ylims[0],ylims[1])))

    def on_new_cursor(self,event):
        self.plotFrame.var_vx.set(event.x)
        self.plotFrame.var_vy.set(event.y)
        self.plotFrame.image_plot.plot_new_cursor((event.x, event.y))

    def on_select_new_background(self):
        new_selection=self.plotFrame.image_plot.toggle_selector()
        if new_selection is not None:
            self.analysis.set_background(new_selection)
            if self.plotFrame.show_background["state"]=="disabled":
                self.plotFrame.show_background.configure(state=tk.NORMAL)
                self.plotFrame.check_background_correction.configure(state=tk.NORMAL)
    def on_show_background(self):
        self.plotFrame.image_plot.toggle_selector(show_only=True)
    def on_back_to_default(self):
        print("on back to default")
    
    def analyze_one_shot(self):
        print("analyze  shot")

    def delete_shot(self):
        if len(self.fileFrame.list_images.curselection())==0 or len(self.fileFrame.list_runs.curselection())==0:
            return
        image_name=self.fileFrame.list_images.get(self.fileFrame.list_images.curselection()[0])
        run_name=self.fileFrame.list_runs.get(self.fileFrame.list_runs.curselection()[0])
        timestamp=image_name[:6]
        answer = askyesno("Delete shot {}".format(timestamp), "Are you sure you want to delete this shot ?")
        if not answer:
            return
        self.remove_image_from_disk(run_name,image_name)
        
    def on_browse(self):
        selected_path=tk.filedialog.askdirectory(initialdir=config.config_parser["filesystem"]["passerelle_path"], title="Select run", mustexist=True )
        selected_path=os.path.normpath(selected_path)
        splitted=selected_path.split(os.path.sep)
        print(splitted)
        try: 
            # day=datetime.date(int(splitted[-3]),int(splitted[-2]), int(splitted[-1]))
            day = datetime.datetime.strptime(splitted[-1],'%d%b%Y').date()
        except:
            tk.messagebox.showerror(title="Error",message="{}\nis not a valid run path".format(selected_path))
            return
        self.close()
        self.parent.destroy()
        new_window(day)

    def analyze_image(self, image):
        run=self.fileFrame.list_runs.get(self.fileFrame.list_runs.curselection()[0])
        path_to_image=self.get_path_to_image(run, image)
        if self.analysis is None:
            self.analysis=analysis.Analysis(path_to_image, self.plotFrame)
        else: 
            self.analysis.update_analysis(path_to_image)
        self.analysis.plot_and_process()
        #If the camera changed we set the labels to the new value
        if self.analysis.camera_name!=self.plotFrame.var_cam_name.get():
            self.plotFrame.var_cam_name.set(self.analysis.camera_name)
            eff_pixel_size=float(config.config_parser[self.analysis.camera_name]["pixelsize"])/float(config.config_parser[self.analysis.camera_name]["magnification"])
            self.plotFrame.var_pixel_size.set("{:.2f}".format(eff_pixel_size))
        
        
    def close(self):
        #What to do when closing
        self.backend.stop_images_watchdog()
        self.backend.stop_runs_watchdog()
        print("close")



def new_window(day=None): 
    def close():
        main.close()
        root.destroy()
    root = tk.Tk()
    main=MainApplication(root, day)
    root.title("La puissance du GUI")
    #Close everything when window is closed
    root.protocol("WM_DELETE_WINDOW",close)
    root.mainloop()
if __name__ == "__main__":
    new_window()
    