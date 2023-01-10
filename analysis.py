from config import config_parser
import numpy as np
import cv2 as cv
import os 
import scipy.signal
from scipy.optimize import curve_fit
import rb
import tifffile as tiff

def read_image(path):
    try: 
        img=np.array(tiff.imread(path),dtype=np.float32)
        if len(img.shape)==3:
            img=img[0]
    except cv.error as e:
        # inspect error object
        print(e)
        for k in dir(e):
            if k[0:2] != "__":
                print("e.%s = %s" % (k, getattr(e, k)))
    return img
class Analysis:
    def __init__(self, path, plotFrame):
        self.plotFrame=plotFrame
        vx=self.plotFrame.var_vx.get()
        vy=self.plotFrame.var_vy.get()
        xmin=self.plotFrame.var_xmin.get()
        ymin=self.plotFrame.var_ymin.get()
        xmax=self.plotFrame.var_xmax.get()
        ymax=self.plotFrame.var_ymax.get()
        self.fixed_cursor = self.plotFrame.var_fixed_cursors.get()
        self.fix_colorbar=self.plotFrame.var_fix_cbar.get()
        self.folder_path=path
        self.absorption_picture=None
        self.camera_name=None
        self.ROI=np.s_[ymin: ymax, xmin: xmax] if (ymax > ymin and xmax>xmin) else np.s_[:,:]
        self.background=None #Background to normalize images for pixel count
        self.background_correction=self.plotFrame.var_background_correction.get() # Wether we should do background correction
        self.fit_params=None
        self.gauss_fit=self.plotFrame.var_gauss_fit.get()
        self.cursor= [vx, vy] if self.fixed_cursor else None
        self.cbar_bounds= None
        
    def update_analysis(self, path):
        vx=self.plotFrame.var_vx.get()
        vy=self.plotFrame.var_vy.get()
        xmin=self.plotFrame.var_xmin.get()
        ymin=self.plotFrame.var_ymin.get()
        xmax=self.plotFrame.var_xmax.get()
        ymax=self.plotFrame.var_ymax.get()
        self.fixed_cursor = self.plotFrame.var_fixed_cursors.get()
        self.fix_colorbar=self.plotFrame.var_fix_cbar.get()
        self.folder_path=path
        self.ROI=np.s_[ymin: ymax, xmin: xmax] if (ymax > ymin and xmax>xmin) else np.s_[:,:]
        self.gauss_fit=self.plotFrame.var_gauss_fit.get()
        self.cursor= [vx, vy] if self.fixed_cursor else None
        self.background_correction=self.plotFrame.var_background_correction.get()

    def set_background(self, new_selection):
        new_selection=list(map(int, new_selection))
        self.background=np.s_[new_selection[0]:new_selection[1], new_selection[2]:new_selection[3]]
        
    def calculate_atom_number_count(self, pixel_size):
        return np.nansum(self.absorption_picture[self.ROI])*pixel_size**2/rb.sigma0
    def set_camera_and_absorption_picure(self):
        threshold=0.02
        #We set the camera_name
        self.camera_name=os.path.basename(self.folder_path).split("_")[2]
        dict_pictures=self.open_picture()
        for image in dict_pictures.values():
            print(image.shape)
        transmission=(dict_pictures["atoms"]-dict_pictures["background"])/(dict_pictures["no atoms"]-dict_pictures["background"])
        burned_pixels=transmission <=0
        transmission[burned_pixels] = float("nan")
        bad_pixels=dict_pictures["no atoms"]<np.nanmax(dict_pictures["no atoms"])*threshold
        transmission[bad_pixels] = float("nan")
        od = np.nan_to_num(-np.log(transmission), nan=np.nan, posinf=np.nan, neginf=np.nan)
        self.absorption_picture=od
        return od
    def open_picture(self):
        #The suffixes we have to add to the folder name to obtain the corresponding pictures
        print(self.camera_name)
        if self.camera_name=="Princeton":
            with_atoms_name="frames_0001.tiff"
            no_atoms_name="frames_0002.tiff"
            background_name="frames_0003.tiff"
        else:
            with_atoms_name="frames_0000.tiff"
            no_atoms_name="frames_0001.tiff"
            background_name="frames_0002.tiff"
        img_with_atoms=read_image(os.path.join(self.folder_path, with_atoms_name)) #we load the images
        
                    
        img_no_atoms=read_image(os.path.join(self.folder_path, no_atoms_name))
        ## Remove the offest
        if  (not self.gauss_fit) and (self.background is not None) and (self.background_correction):
            ratio = np.nanmean(img_no_atoms[self.background]
                                    /img_with_atoms[self.background])
            img_no_atoms = img_no_atoms/ratio
            print("Correction ratio is {}".format(ratio))
        ##
        img_background=read_image(os.path.join(self.folder_path, background_name))
        return {"atoms": img_with_atoms, 'no atoms': img_no_atoms, 'background':img_background}

    def set_cursor_and_cbar(self, center=None, offset=0):
        square = (1/16)*np.ones((4,4))
        if not self.fix_colorbar or not self.fixed_cursor:
            if center is None: 
                coarse_img = scipy.signal.convolve2d(self.absorption_picture[self.ROI], square, mode = 'same')
                max_od = np.nanmax(coarse_img)
                min_od = np.nanmin(coarse_img)
                ymax2, xmax2 = np.unravel_index(coarse_img.argmax(), coarse_img.shape)
                if self.ROI[0].start is not None :
                    ymax2 = ymax2 + self.ROI[0].start
                if self.ROI[1].start is not None :
                    xmax2 = xmax2 + self.ROI[1].start
            else:
                ymax2, xmax2 = center[1], center[0]
                max_od=self.absorption_picture[center[1], center[0]]
                min_od=offset

            if not self.fixed_cursor: 
                self.cursor = [xmax2, ymax2]
                self.plotFrame.var_vx.set(xmax2)
                self.plotFrame.var_vy.set(ymax2)
            if not self.fix_colorbar:
                self.cbar_bounds= [min_od, max_od]
            

    def plot_and_process(self):
        abs_picture=self.set_camera_and_absorption_picure()
        if not self.gauss_fit:
            self.set_cursor_and_cbar()
        pixel_size = float(config_parser[self.camera_name]["pixelsize"])/float(config_parser[self.camera_name]["magnification"])*1e-6
        if self.gauss_fit:
            fitted_picture, A, center_x, center_y, sigma_x, sigma_y, offset =self.fit_picture()
            atom_number= calculate_atom_number_fit(A, sigma_x, sigma_y, pixel_size)
            self.set_cursor_and_cbar(center=[int(center_x),int(center_y)], offset=offset)

        else:
            fitted_picture=None
            atom_number = self.calculate_atom_number_count(pixel_size)
        
        self.plotFrame.var_nat.set("{:.2e}".format(atom_number))
        self.plotFrame.image_plot.plot_im(abs_picture, cursor=self.cursor, cbar_bounds=self.cbar_bounds, fitted_picture=fitted_picture)
    
    def fit_picture(self):
        y, x=np.indices(self.absorption_picture.shape)
        popt=fit_gaussian_2D(x[self.ROI], y[self.ROI], self.absorption_picture[self.ROI], bin=5)
        return rot_gaussian(x, y, *popt), popt[0], popt[1], popt[2], popt[3], popt[4], popt[5] #we return the image and A, sigma_x, sigma_y


 #Fit functions

def rebin(a, bin):
    a=a[0: (a.shape[0]//bin)*bin, 0: (a.shape[1]//bin)*bin]
    return np.nanmean(np.nanmean(a.reshape(a.shape[0]//bin, bin, a.shape[1]//bin,bin),axis=-1), axis=-2)

def rotation(x, y, theta):
    angle=np.deg2rad(theta)
    return (np.cos(angle)*x+np.sin(angle)*y, -np.sin(angle)*x + np.cos(angle)*y)

#Simple 2d gaussian
def gaussian(x, y ,A, sigma_x, sigma_y, offset):
    return A*np.exp(-((x)**2/(2*sigma_x**2) + (y)**2/(2*sigma_y**2))) +offset

#2d gaussian with rotation
def rot_gaussian(x,y,A,x_0,y_0, sigma_x, sigma_y, offset, theta):
    x_rot, y_rot=rotation(x-x_0, y-y_0,theta)
    return gaussian(x_rot,y_rot,A,sigma_x, sigma_y, offset)

#finds an initial guess for a 2d gaussian fit
def find_initial_guess(x,y,z):
    offset=np.min(z)
    z=z-offset
    A=np.max(z)
    #calculate the centroid
    centroid_x, centroid_y=np.average(x, weights=z),np.average(y, weights=z)
    cov=np.zeros((2,2))
    #calculate the covariance matrix to find the sigma_x, sigma_y and the angle
    cov[0,0]=np.average((x)**2, weights=z)-centroid_x**2
    cov[1,1]=np.average((y)**2, weights=z) - centroid_y**2
    cov[0,1]=np.average(x*y, weights=z) - centroid_x*centroid_y
    cov[1,0]=cov[0,1]
    #We diagonalize the covariance matrix
    eig=np.linalg.eigh(cov)
    sigma_x, sigma_y=np.sqrt(eig[0])
    ##The index tells us the eigenvector that has 2 values of the same sign i.e (cos, sin)
    index=0
    if eig[1][0,0]*eig[1][0,1]>0:
        index=0
    else:
        index=1
    #We take the arctan of the ratio of the compenents of the eigenvector (cos, sin) to get the angle
    theta=np.rad2deg(np.arctan(eig[1][index, 1]/eig[1][index,0]))
    return (A,centroid_x,centroid_y,sigma_x, sigma_y, offset, theta)

def fit_gaussian_2D(x,y,z,bin=1, angle=None):
    #Get initial guess
    x_min, x_max=np.min(x), np.max(x)
    y_min, y_max=np.min(y), np.max(y)
    if not bin==1:
        x=rebin(x, bin)
        y=rebin(y, bin)
        z=rebin(z,bin) 
    #We clean the images by removing the NAN 
    cleaning=np.isfinite(z)
    x=x[cleaning]
    y=y[cleaning]
    z=z[cleaning]
    initial_guess=find_initial_guess(x,y,z)
    if angle is None:
        func_to_fit = lambda x, A,x_0,y_0, sigma_x, sigma_y, offset, theta : rot_gaussian(*x, A,x_0,y_0, sigma_x, sigma_y, offset,theta)
    else:
        func_to_fit = lambda x, A,x_0,y_0, sigma_x, sigma_y, offset : rot_gaussian(*x, A,x_0,y_0, sigma_x, sigma_y, offset, angle)
    min_z,max_z=np.min(z), np.max(z)
    try :
        if angle is None:
            popt,_ =curve_fit(func_to_fit, [x.ravel(),y.ravel()], z.ravel(), p0=initial_guess, bounds=([0,x_min,y_min,0,0,min_z,0],[2*(max_z-min_z), x_max,y_max, x_max, y_max, max_z,89.99]), maxfev=50)
            return popt
        else: 
            initial_guess=initial_guess[:-1]
            popt,_ =curve_fit(func_to_fit, [x.ravel(),y.ravel()], z.ravel(), p0=initial_guess, bounds=([0,x_min,y_min,0,0,min_z],[2*(max_z-min_z), x_max,y_max, x_max, y_max, max_z]), maxfev=50)
            return np.append(popt, angle)
    except Exception as e:
        print("Could not fit : {}".format(e))
        empty_array=np.empty(len(initial_guess))
        empty_array[:]=np.NAN
        return empty_array
    


def calculate_atom_number_fit(A, sigma_x, sigma_y, pixel_size):
    return A*2*np.pi*sigma_x*sigma_y*pixel_size**2/rb.sigma0
