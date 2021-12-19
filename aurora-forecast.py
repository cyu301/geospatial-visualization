# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

import json
from urllib.request import urlopen
from datetime import datetime

from cartopy import crs as ccrs
from cartopy.feature.nightshade import Nightshade

def fetch_forecast():  
    """
    Get the latest Aurora Forecast from https://www.swpc.noaa.gov.

    Returns
    -------
    img : numpy array
        The pixels of the image in a numpy array.
    img_proj : cartopy CRS
        The rectangular coordinate system of the image.
    img_extent : tuple of floats
        The extent of the image ``(x0, y0, x1, y1)`` referenced in
        the ``img_proj`` coordinate system.
    origin : str
        The origin of the image to be passed through to matplotlib's imshow.
    dt : datetime
        Time of forecast validity.

    """    
    
    # coodinate range: 
    # Longitude [0,359] 360 values 
    # Latitude [-90,90] 181 values
    
    # GitHub gist to download the example data from 
    url = 'https://raw.githubusercontent.com/cyu301/geospatial-visualization/main/data/ovation_aurora_latest.json'
    
    # To plot the current forecast instead, uncomment the following line
    # Note: NOAA may have upgrade their format
    # url = 'https://services.swpc.noaa.gov/json/ovation_aurora_latest.json'
    f = json.load(urlopen(url))
        
    forecast_time = datetime.strptime(f['Forecast Time'], '%Y-%m-%dT%H:%M:%SZ')
    observation_time = datetime.strptime(f['Observation Time'], '%Y-%m-%dT%H:%M:%SZ')
    
    coordinates = np.array(f['coordinates'])
    img = np.zeros((181,360))
    for longi,lati,aur in coordinates:
        img[int(lati+90),longi] = aur
    
    img_proj = ccrs.PlateCarree()
    img_extent = (-180, 180, -90, 90)
    
    return img,img_proj,img_extent,'lower',[forecast_time, observation_time]

def aurora_cmap():
    """Return a colormap with aurora like colors"""
    stops = {'red': [(0.00, 0.1725, 0.1725),
                     (0.50, 0.1725, 0.1725),
                     (1.00, 0.8353, 0.8353)],

             'green': [(0.00, 0.9294, 0.9294),
                       (0.50, 0.9294, 0.9294),
                       (1.00, 0.8235, 0.8235)],

             'blue': [(0.00, 0.3843, 0.3843),
                      (0.50, 0.3843, 0.3843),
                      (1.00, 0.6549, 0.6549)],

             'alpha': [(0.00, 0.0, 0.0),
                       (0.50, 1.0, 1.0),
                       (1.00, 1.0, 1.0)]}

    return LinearSegmentedColormap('aurora', stops)

def draw_aurora():
    """Draw the current aurora predictions."""
    img, crs, extent, origin, dt = fetch_forecast()
    
    fig = plt.figure(figsize=[10, 5])

    # Choose to plot in an Orthographic projection as it looks natural
    # and the distortion is relatively small around the poles where
    # the aurora is most likely.
    
    fig.suptitle(f'Observation Time: {dt[1]} UTC\nForecast time: {dt[0]} UTC\n')
    
    # ax1 for Northern Hemisphere
    ax1 = fig.add_subplot(1, 2, 1, projection=ccrs.Orthographic(0, 90))
    ax1.set_title('Northern Hemisphere')
    
    # ax2 for Southern Hemisphere
    ax2 = fig.add_subplot(1, 2, 2, projection=ccrs.Orthographic(180, -90))
    ax2.set_title('Southern Hemisphere')
    
    for ax in [ax1, ax2]:
        ax.coastlines(zorder=3)
        ax.stock_img()
        ax.gridlines()
        ax.add_feature(Nightshade(dt[0]))
        ax.imshow(img, vmin=0, vmax=100, transform=crs,
                  extent=extent, origin=origin, zorder=2,
                  cmap=aurora_cmap())

    plt.show()
    
if __name__ == '__main__':
    draw_aurora()