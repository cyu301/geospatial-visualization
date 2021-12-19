# -*- coding: utf-8 -*-

from urllib.request import urlopen
from io import StringIO

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import shapely.geometry as sgeom

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

def global_loc(lat,lon):
    '''Change to global location with positive and negative values.'''
    glo_lat = float(lat[:-1]) if lat[-1]=='N' else -float(lat[:-1])
    glo_lon = float(lon[:-1]) if lon[-1]=='E' else -float(lon[:-1])
    return glo_lon,glo_lat
    
def fetch_cyclone(h2):
    '''
    Loop through the hurdat2 format and return a dict with 
    information about the path of cyclone in each year.
    '''
    # move back to the starter of file
    h2.seek(0)
    
    # basin tag for h2 dataset
    basin_tag = {'AL':'Atlantic','EP':'Northeast Pacific','CP':'North Central Pacific'}
    
    # useful item in the loop
    cyclone = {}
    year_dict = {}
    cyclone_list = [[],[]]
    current_year = 1644    
    line_count = 0
    unnamed_count = 0
    
    for line in h2:
        splited = line.split(',')
        
        # case head
        if line_count == 0:
            if splited[0][:2] in basin_tag:
                year = int(splited[0][-4:])
                
                # append year_dict to the whole
                if year!=current_year:
                    if len(year_dict)>0:
                        cyclone[current_year] = year_dict
                        year_dict = {}
                    current_year = year
                    unnamed_count = 0
                    
                cyclone_name = splited[1].replace(' ','')
                
                # deal with the case unnamed
                if cyclone_name == 'UNNAMED':
                    cyclone_name = 'UNNAMED' + f'-{unnamed_count}'
                    unnamed_count += 1
                    
                line_count = int(splited[2])
        
        #case data
        elif line_count >0:
            lon,lat = global_loc(splited[4], splited[5])
            cyclone_list[0].append(lon)
            cyclone_list[1].append(lat)

            line_count -= 1
            
            # append cyclone data to year_dict
            if line_count == 0:
                year_dict[cyclone_name] = cyclone_list
                cyclone_list = [[],[]]
            
    # add final year data
    cyclone[current_year] = year_dict
    return cyclone

def get_cyclone_names(year):
    '''Return the names of all the cyclone in the given year.'''
    return list(dic[year].keys())

def get_cyclone_path(year,name):
    '''Return the path of the given cyclone in the given year.'''
    lons = dic[year][name][0]
    lats = dic[year][name][1]
    return lons,lats

def draw(year,name):
    '''Draw the cyclone and intersected states.'''
    fig = plt.figure()
    # to get the effect of having just the states without a map "background"
    # turn off the background patch and axes frame
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal(),
                      frameon=False)
    ax.patch.set_visible(False)

    ax.set_extent([-125, -66.5, 20, 50], ccrs.Geodetic())

    shapename = 'admin_1_states_provinces_lakes'
    states_shp = shpreader.natural_earth(resolution='110m',
                                         category='cultural', name=shapename)

    lons, lats = get_cyclone_path(year,name)

    ax.set_title(f'US States which intersect the track of '
                 f'Hurricane {name} {year}')

    # turn the lons and lats into a shapely LineString
    track = sgeom.LineString(zip(lons, lats))

    # buffer the linestring by two degrees (note: this is a non-physical distance)
    track_buffer = track.buffer(2)

    def colorize_state(geometry):
        facecolor = (0.9375, 0.9375, 0.859375)
        if geometry.intersects(track):
            facecolor = 'red'
        elif geometry.intersects(track_buffer):
            facecolor = '#FF7E00'
        return {'facecolor': facecolor, 'edgecolor': 'black'}

    ax.add_geometries(
        shpreader.Reader(states_shp).geometries(),
        ccrs.PlateCarree(),
        styler=colorize_state)

    ax.add_geometries([track_buffer], ccrs.PlateCarree(),
                      facecolor='#C8A2C8', alpha=0.5)
    ax.add_geometries([track], ccrs.PlateCarree(),
                      facecolor='none', edgecolor='k')

    # make two proxy artists to add to a legend
    direct_hit = mpatches.Rectangle((0, 0), 1, 1, facecolor="red")
    within_2_deg = mpatches.Rectangle((0, 0), 1, 1, facecolor="#FF7E00")
    labels = ['State directly intersects\nwith track',
              'State is within \n2 degrees of track']
    ax.legend([direct_hit, within_2_deg], labels,
              loc='lower left', bbox_to_anchor=(0.025, -0.1), fancybox=True)

    plt.show()
    
def path(year):
    '''Draw all the cyclone in the given year on the atlantic ocean.'''
    # background
    fig = plt.figure(figsize=(12,12))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # use latitude and longitude
    ax.set_extent([-105, -25, 10, 50], crs=ccrs.PlateCarree())

    # title
    ax.set_title(f'Cyclone Path on the Atlantic Ocean in year {year}',fontsize=16)

    # set features
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.RIVERS)
    ax.add_feature(cfeature.LAKES, alpha=0.5)

    for name in dic[year].keys():
        lons,lats = get_cyclone_path(year,name)

        # turn the lons and lats into a shapely LineString
        track = sgeom.LineString(zip(lons, lats))
        ax.add_geometries([track], ccrs.PlateCarree(),facecolor='none', edgecolor='r')
        
        #add buffer
        track_buffer = track.buffer(0.1)
        ax.add_geometries([track_buffer], ccrs.PlateCarree(),facecolor='#C8A2C8', alpha=0.5)
    plt.show()

if __name__ == '__main__':
    
    # GitHub gist to download the example data from 
    url = 'https://raw.githubusercontent.com/cyu301/geospatial-visualization/main/data/hurdat2-1851-2020-052921.txt'
    
    # To plot the latest forecast instead, uncomment the following line
    # Note: NOAA may have changed the url
    # origin hurdat2 data
    #url = 'https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2020-052921.txt'

    # hurdat2 data for pacific area
    #url = 'https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2020-043021a.txt'

    h2 = StringIO(urlopen(url).read().decode('utf-8'))
    dic = fetch_cyclone(h2)
    
    # draw two plots
    draw(2020,'DELTA')
    path(2020)