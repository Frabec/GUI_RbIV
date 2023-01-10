from optparse import Option
import tkinter as tk
from matplotlib.backends.backend_tkagg import  NavigationToolbar2Tk
from figure import Image_Plot


def give_focus(event):
    l = event.widget
    l.focus_set()    


def destroying(event):
    w = event.widget
    w.destroy()


###############Custom widgets###############


# Button highlighting when cursor on it
class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
        
# Checkbutton highlighting when cursor on it        
class HoverCheckButton(tk.Checkbutton):
    def __init__(self, master, **kw):
        tk.Checkbutton.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
class FileFrame(tk.Frame):
    def __init__(self, parent, mainapp,  *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.mainapp=mainapp
        ## Tkinter Vars ##
        self.var_day_in_list = tk.StringVar()
        self.var_watch_camera = tk.IntVar()  
        self.var_live_update = tk.IntVar()
        #Init TkVars
        self.init_tk_vars()
        ## Tkinter widgets ##
        # List runs and its scrollbars #
        self.label_list_runs = tk.Label(self, text = 'List run ', font = 'CMUBright')
        self.scrollbar_runs_x = tk.Scrollbar(self, orient="horizontal")
        self.scrollbar_runs_y = tk.Scrollbar(self)
        self.list_runs = tk.Listbox(self ,xscrollcommand=self.scrollbar_runs_x.set,yscrollcommand = self.scrollbar_runs_y.set, font = 'CMUBright', activestyle = 'dotbox', height = 15, width = 25, selectbackground = 'LightSkyblue1', selectforeground = 'black', exportselection=False, selectmode='single') 
        self.label_list_runs.grid(row = 1, column = 1, sticky='w')
        self.list_runs.grid(row = 2, column = 1, rowspan = 11, sticky = 'wn') 
        self.scrollbar_runs_x.config( command = self.list_runs.xview )
        self.scrollbar_runs_x.grid( row = 13, column = 1, sticky = 'wne')
        self.scrollbar_runs_y.config( command = self.list_runs.yview )
        self.scrollbar_runs_y.grid( row = 2, rowspan = 11, column = 2, sticky = 'nsw', padx=(0,20))
        self.list_runs.bind('<Enter>', give_focus)
        self.list_runs.bind("<Button-1>", give_focus)
        self.list_runs.bind('<<ListboxSelect>>', self.mainapp.on_new_run_selected)
        self.list_runs.bind("<Button-3>", self.mainapp.copy_run_selection)
        # List images and its scrollbars #
        self.label_list_images = tk.Label(self, text = 'List images', font = 'CMUBright')
        self.label_day_in_list = tk.Label(self, font = 'CMUBright',textvariable=self.var_day_in_list)
        self.scrollbar_images_x = tk.Scrollbar(self, orient = 'horizontal')
        self.scrollbar_images_y = tk.Scrollbar(self)
        self.list_images = tk.Listbox(self, xscrollcommand = self.scrollbar_images_x.set, yscrollcommand = self.scrollbar_images_y.set, font = 'CMUBright', activestyle = 'dotbox', height = 15, width = 75, selectbackground = 'LightSkyblue1', selectforeground = 'black', exportselection=False, selectmode='single') 
        self.label_list_images.grid(row = 1, column = 3, sticky='w')
        self.label_day_in_list.grid(row = 1, column = 4, sticky='w')
        self.list_images.grid(row = 2, column = 3, rowspan = 11,columnspan=2, sticky = 'wne') 
        self.scrollbar_images_y.config( command = self.list_images.yview )
        self.scrollbar_images_y.grid( row = 2, rowspan = 11, column = 5, sticky = 'nsw')
        self.scrollbar_images_x.config( command = self.list_images.xview )
        self.scrollbar_images_x.grid( row = 13, column = 3, columnspan=2, sticky = 'wne')
        self.list_images.bind('<Enter>', give_focus)
        self.list_images.bind("<Button-1>", give_focus)
        self.list_images.bind('<<ListboxSelect>>', self.mainapp.on_new_image_selected)
        self.list_images.bind("<Button-3>", self.mainapp.copy_image_selection)
        # List options #
        check_live_update = HoverCheckButton(self, text='Display new', variable=self.var_live_update, font = 'CMUBright', activebackground = 'LightSkyblue1')
        check_live_update.grid(row=7, column = 6, columnspan=2, sticky= 'w')
        check_watch_camera = HoverCheckButton(self, text='Watch camera', variable=self.var_watch_camera, font = 'CMUBright', activebackground = 'LightSkyblue1')
        check_watch_camera.grid(row=8, column = 6, columnspan=2, sticky= 'w')
        button_refresh = HoverButton(self, text = 'Refresh', width = 11, activebackground = 'LightSkyblue1', command = self.mainapp.analyze_one_shot)
        button_refresh.grid(row=3, column = 6, columnspan=2, sticky= 'ne')
        button_last = HoverButton(self, text = 'Last', width = 11, activebackground = 'LightSkyblue1', command = self.mainapp.on_last_image)
        button_last.grid(row=4, column = 6, columnspan=2, sticky= 'ne')
        button_browselist = HoverButton(self, text = 'Browse list', width = 11, activebackground = 'LightSkyblue1', command = self.mainapp.on_browse)
        button_browselist.grid(row=5, column = 6, columnspan=2, sticky= 'ne')

    
    # initialization of tk_vars
    def init_tk_vars(self):
        #default value of variables
        LIVE_UPDATE = 1
        self.var_day_in_list.set(self.mainapp.day)
        self.var_live_update.set(LIVE_UPDATE)

class PlotFrame(tk.Frame):
    def __init__(self, parent, mainapp,*args, **kwargs):
        tk.Frame.__init__(self, parent,*args, **kwargs)
        self.mainapp=mainapp
        ## Tkinter Vars ##
        self.var_gauss_fit = tk.IntVar()
        self.var_fixed_cursors=tk.IntVar()
        self.var_background_correction=tk.IntVar()
        self.var_vx=tk.IntVar()
        self.var_vy=tk.IntVar()
        self.var_xmin = tk.IntVar()
        self.var_xmax = tk.IntVar()
        self.var_ymin = tk.IntVar()
        self.var_ymax = tk.IntVar() 
        self.var_nat = tk.StringVar()
        self.var_fix_cbar = tk.IntVar()
        self.var_cam_name = tk.StringVar()
        self.var_pixel_size =tk.StringVar()
        
        #Init TkVars
        self.init_tk_vars()

        #We create the labelframes that will contain our widgets
        self.ROI_frame=tk.LabelFrame(self, text="ROI")
        self.Nat_frame=tk.LabelFrame(self, text="Atom number")
        self.Option_frame=tk.Frame(self)
        self.Cursor_frame=tk.LabelFrame(self, text="Cursor")
        self.Camera_frame=tk.Frame(self)
        self.Background_frame=tk.LabelFrame(self, text="Background for pixel count")
        frames_padding=20
        self.ROI_frame.grid(row=1, column=10, sticky="we", padx=(frames_padding,0))
        self.Cursor_frame.grid(row=2, column=10, sticky="we", padx=(frames_padding,0))
        self.Nat_frame.grid(row=3, column=10, sticky="we", padx=(frames_padding,0))
        self.Background_frame.grid(row=4, column=10, padx=(frames_padding,0))
        self.Option_frame.grid(row=5, column=10, padx=(frames_padding,0))
        self.Camera_frame.grid(row=6, column=10, padx=(frames_padding,0))
        

        #  ROI  #
        self.label_xmin = tk.Label(self.ROI_frame, text='xmin', font = 'CMUBright')
        self.label_xmax = tk.Label(self.ROI_frame, text='xmax', font = 'CMUBright') 
        self.label_ymin = tk.Label(self.ROI_frame, text='ymin', font = 'CMUBright')
        self.label_ymax = tk.Label(self.ROI_frame, text='ymax', font = 'CMUBright')  
        self.button_set_view_as_ROI = HoverButton(self.ROI_frame, text="Set to current view", width=15, activebackground = 'LightSkyblue1', command = self.mainapp.on_set_view_as_ROI)
        self.entry_cut_xmin = tk.Entry(self.ROI_frame, textvariable = self.var_xmin, width = 6)
        self.entry_cut_xmax= tk.Entry(self.ROI_frame, textvariable = self.var_xmax, width = 6) 
        self.entry_cut_ymin = tk.Entry(self.ROI_frame, textvariable = self.var_ymin, width = 6)
        self.entry_cut_ymax = tk.Entry(self.ROI_frame, textvariable = self.var_ymax, width = 6)
        self.label_xmin.grid(row = 0, column = 0, sticky = 'w')  
        self.entry_cut_xmin.grid(row = 0, column = 1, sticky = 'w')
        self.label_ymin.grid(row = 0, column = 3, sticky = 'e')
        self.entry_cut_ymin.grid(row =0 , column = 4, sticky = 'e')
        self.label_xmax.grid(row = 1, column = 0, sticky = 'w')  
        self.entry_cut_xmax.grid(row = 1, column = 1, sticky = 'w')
        self.label_ymax.grid(row = 1, column = 3, sticky = 'e')
        self.entry_cut_ymax.grid(row = 1 , column = 4, sticky = 'e')
        self.button_set_view_as_ROI.grid(row=2, column=2,columnspan=2, sticky='n')
        self.ROI_frame.grid_columnconfigure(2, weight=10)
        button_default = HoverButton(self, text = 'Back to\ndefault', width = 15, activebackground = 'LightSkyblue1', command = self.mainapp.on_back_to_default)
        # button_default.grid(row=11, column = 12, columnspan=1, sticky= 'n')

        #  Cursor #
        self.label_x = tk.Label(self.Cursor_frame, text='Position x', font = 'CMUBright') 
        self.label_y = tk.Label(self.Cursor_frame, text='Position y', font = 'CMUBright') 
        self.entry_cut_x = tk.Entry(self.Cursor_frame, textvariable = self.var_vx, width = 6) 
        self.entry_cut_y = tk.Entry(self.Cursor_frame, textvariable = self.var_vy, width = 6)
        self.label_x.pack(side="left") 
        self.entry_cut_x.pack(side="left")
        self.entry_cut_y.pack(side="right")
        self.label_y.pack(side="right")
        #Camera and image information
        self.label_legend_camera_name=tk.Label(self.Camera_frame, text = 'Cam name:', font = 'CMUBright')
        self.label_legend_pixel_size=tk.Label(self.Camera_frame, text = 'Eff pixel size (µm):', font = 'CMUBright')
        self.label_camera_name=tk.Label(self.Camera_frame, textvariable=self.var_cam_name, font=("CMUBright",15))
        self.label_pixel_size=tk.Label(self.Camera_frame, textvariable=self.var_pixel_size, font=("CMUBright",15))
        self.label_legend_camera_name.grid(row=0, column=0, sticky='n', padx=(0,10))
        self.label_legend_pixel_size.grid(row=0, column=1, sticky='n', padx=(10,0))
        self.label_camera_name.grid(row=1, column=0, sticky='n')
        self.label_pixel_size.grid(row=1, column=1, sticky='n')
        # Nat #
        self.label_atom_number= tk.Label(self.Nat_frame, textvariable = self.var_nat, font = ('CMUBright',30), bg = 'white', height = 2, width = 10)
        self.label_atom_number.pack(fill=tk.BOTH)
        
        # Options #
        self.check_gauss_fit = HoverCheckButton(self.Option_frame, text='Gaussian fit', variable = self.var_gauss_fit, font = 'CMUBright', activebackground = 'LightSkyblue1')
        self.check_fix_colorbar = HoverCheckButton(self.Option_frame, text= 'Fix colorbar', variable= self.var_fix_cbar, font = 'CMUBright', activebackground = 'LightSkyblue1')
        self.check_fixed_cursor = HoverCheckButton(self.Option_frame, text='Fixed cursor', variable=self.var_fixed_cursors, font = 'CMUBright', activebackground = 'LightSkyblue1')
        self.check_background_correction = HoverCheckButton(self.Option_frame, text='Background correction', variable=self.var_background_correction,font = 'CMUBright', activebackground = 'LightSkyblue1', state=tk.DISABLED)
        self.check_gauss_fit.grid(row=0, column = 0, sticky= 'w')
        self.check_fix_colorbar.grid(row=1, column=0, sticky='w')
        self.check_fixed_cursor.grid(row=2, column = 0, sticky= 'w')
        self.check_background_correction.grid(row=3, column=0, sticky='w')

        # Background selection #
        self.select_background = HoverButton(self.Background_frame, text='Select new background', command=self.mainapp.on_select_new_background)
        self.show_background = HoverButton(self.Background_frame, text='Show current background', state=tk.DISABLED, command=self.mainapp.on_show_background)
        self.select_background.pack(side="left")
        self.show_background.pack(side="right")

        # Image display #
        # self.grid_columnconfigure(1, weight=30)
        # self.grid_columnconfigure(2, weight=30)
        # self.grid_rowconfigure(15, weight=30)
        self.label_abs_image = tk.Label(self, text = 'Absorption image', font = 'CMUBright')
        self.label_abs_image.grid(row = 0, column = 1)
        self.label_abs_cuts = tk.Label(self, text = 'Cuts', font = 'CMUBright')
        self.label_abs_cuts.grid(row = 0, column = 2)
        self.image_plot = Image_Plot(self)
        self.image_plot.canvas1.get_tk_widget().grid(row = 1, column =1, rowspan = 25, sticky ='w')
        # self.image_plot.canvas1.get_tk_widget().configure(curTrue)
        self.image_plot.canvas1.draw()
        self.toolbarFrame = tk.Frame(master=self)
        self.toolbarFrame.grid(row=32,column=1, columnspan=2,sticky ='w')
        self.toolbar = NavigationToolbar2Tk(self.image_plot.canvas1, self.toolbarFrame)      
        self.image_plot.canvas2.get_tk_widget().grid(row = 1, column =2, rowspan = 25)#, sticky ='w')
        # self.image_plot.canvas2.get_tk_widget().configure(takefocus=True)
        self.image_plot.canvas2.draw()
        self.image_plot.canvas1.get_tk_widget().bind("<Enter>", give_focus) #give focus to plot when mouse pointer on it 
            # initialization of tk_vars
    def init_tk_vars(self):
        #default value of variables
        VALUE_NAT = 0
        GAUSS_FIT = 0
        FIXED_CURSOR = 0
        VALUE_X = 0
        VALUE_Y = 0
        VALUE_XMIN = 0
        VALUE_XMAX = 0 
        VALUE_YMIN = 0 
        VALUE_YMAX = 0
        FIX_COLORBAR = 0
        BACKGROUND_CORRECTION = 0
        VAR_CAM_NAME = "Camera"
        VAR_PIXEL_SIZE = "42.0"
        self.var_gauss_fit.set(GAUSS_FIT)
        self.var_fixed_cursors.set(FIXED_CURSOR)
        self.var_background_correction.set(BACKGROUND_CORRECTION)
        self.var_vx.set(str(VALUE_X))
        self.var_vy.set(str(VALUE_Y))
        self.var_xmin.set(str(VALUE_XMIN))
        self.var_ymin.set(str(VALUE_YMIN))
        self.var_xmax.set(str(VALUE_XMAX))
        self.var_ymax.set(str(VALUE_YMAX))
        self.var_nat.set(str(VALUE_NAT))
        self.var_fix_cbar.set(FIX_COLORBAR)
        self.var_cam_name.set(VAR_CAM_NAME)
        self.var_pixel_size.set(str(VAR_PIXEL_SIZE))