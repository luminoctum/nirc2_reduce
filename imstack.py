#!/usr/bin/env python
from nirc2_reduce import coordgrid
import matplotlib.pyplot as plt
import numpy as np

'''Functions to compute filter ratios, extract features at given locations,
generate points to compare against RT codes.
Takes a list of images with I/F already calculated'''

def get_lambda_eff(filt):
    tablef = '/Users/emolter/Python/nirc2_reduce/filter_passbands/vega_fluxes.txt'
    with open(tablef, 'r') as f:
        f.readline() #header line
        for line in f:
            l = line.split(',')
            ft = l[0].strip(', \n')
            wl = float(l[1].strip(', \n'))
            if ft == filt:
                return wl

class Stack:
    
    def __init__(self, fnames):
        '''fnames should be a list of filt_centered.fits files'''
        stack = {} #dict in format filter:CoordGrid object
        for fn in fnames:
            leadstr = fn.split('_')[0]
            stack[leadstr] = coordgrid.CoordGrid(fn, lead_string = leadstr)
        self.stack = stack
        
        '''Make images of filter ratios. For every possible combination of
        filters, compute filt1/filt2 over the image'''
        ratios = {}
        self.filts = list(self.stack.keys())
        self.wls_eff = [get_lambda_eff(filt) for filt in self.filts]
        for i in range(len(self.filts)):
            for j in range(len(self.filts)):
                if i != j:
                    im1 = self.stack[self.filts[i]]
                    im2 = self.stack[self.filts[j]]
                    ratio_key = self.filts[i]+'/'+self.filts[j]
                    ratioim = im1.centered/im2.centered
                    #invalidate points off planet - use h band by default since edge detection usually works faithfully there, but don't fail if no h band
                    if 'h' in self.filts:
                        ratioim[np.isnan(self.stack['h'].lat_g)] = 0 
                    else:
                        ratioim[np.isnan(self.stack[self.filts[0]].lat_g)] = 0 #invalidates points off planet
                    ratios[ratio_key] = ratioim         
        self.ratios = ratios
        print('Image stack object created with filters {}'.format(self.filts))
        
    def extract_point(self, x, y):
        '''Print the I/F value and central wavelength of each filter
        for a given x,y coordinate in the image'''
        fluxes = [self.stack[filt].centered[x,y] for filt in self.filts]
        sort = np.argsort(self.wls_eff)
        print('filter    wl_eff (um)    I/F')
        for j in sort:
            print(self.filts[j] + '    ' + str(self.wls_eff[j]) + '    ' + str(fluxes[j]))
        
    def extract_ratios(self, x, y, which = 'all'):
        '''Print the filter ratios for a given x,y coordinate in the image
        optionally specify which ratios you want as list, 
        e.g. ['kp/h', 'kp/ch4s', 'kp/pabeta']'''
        if which == 'all':
            which = list(self.ratios.keys())
        print('ratio    I/F')
        for rstr in sorted(which):
            flux = self.ratios[rstr][x,y]
            print(rstr + '    ' + str(flux))
        
    def extract_region(self):
        '''Not sure how this one will work yet.
        depends on what type of features need to be modeled'''
        pass
    
    
    
    
    