import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from cartopy import crs as ccrs
import contextily as ctx
import requests
import time
import functools
import cProfile
from mapcompare.sql2gdf import sql2gdf
from mapcompare.misc.pw import password


# Add if saving figure: from datetime import datetime
# Add if using cartopy plotting methods: from cartopy.feature import ShapelyFeature
# Add if using DEMs as basemap: import demload

def timer(func):
    """Print runtime of decorated function. Quick option as alternative to cProfile and snakeviz."""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter() 
        run_time = end_time - start_time
        print(f"\nFinished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

def renderFigure(buildings_in, buildings_out, rivers):

    def getBBox(*gdfs):
        """Return combined bbox of all GDFs in cartopy set_extent format (x0, x1, y0, y1).
        """

        list_of_bounds = []
        for gdf in gdfs:
            gdf_bounds = gdf.total_bounds
            list_of_bounds.append(gdf_bounds)
            
        xmin = np.min([item[0] for item in list_of_bounds])
        xmax = np.max([item[2] for item in list_of_bounds])
        ymin = np.min([item[1] for item in list_of_bounds])
        ymax = np.max([item[3] for item in list_of_bounds])
        
        carto_extent = [xmin, xmax, ymin, ymax]
        
        return carto_extent
    
    # Get number of features per GDF, to display in legend
    buildings_in_no = str(len(buildings_in.index))
    buildings_out_no = str(len(buildings_out.index))
    rivers_no = str(len(rivers.index))

    crs = ccrs.epsg('25833')

    carto_extent = getBBox(buildings_in, buildings_out, rivers) # 8 secs

    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs}, figsize=(20, 10))

    ax.set_extent(carto_extent, crs=crs)
    ax.set_title("Visualisation Task Demo using GeoPandas/Cartopy and contextily" + "\n", fontsize=20)
    
    # Add features to Axes
    
    buildings_in.plot(ax=ax, facecolor='red')
    buildings_out.plot(ax=ax, facecolor='lightgrey', edgecolor='black', linewidth=0.1)
    rivers.plot(ax=ax, facecolor='lightblue', edgecolor='blue', linewidth=0.25)

    """
    # Add contextily basemap
    
    try:
        ctx.add_basemap(ax, crs=rivers.crs.to_string(), source=ctx.providers.Stamen.TerrainBackground)
    except requests.HTTPError:
        print("Contextily: No tiles found. Zoom level likely too high. Setting zoom level to 13.")
        ctx.add_basemap(ax, zoom=13, crs=rivers.crs.to_string(), source=ctx.providers.Stamen.TerrainBackground)
    """
    # OPTIONAL instead of contextily: Add 20m DEMs
    # csvpath = 'c:\Users\grego\OneDrive\01_GIS\11_MSc\00_Project\01_data\02_DEM\DGM20\dgm25_akt.csv'
    # data_dir = '01_data/02_DEM/DGM20/'
    # handles, ax = demload.showDEMs(csvpath, data_dir, carto_extent, ax, crs)
    
    # Legend

    buildings_in_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='red')]
    buildings_out_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightgrey', edgecolor='black', linewidth=0.5)]
    rivers_handle = [mpatches.Rectangle((0, 0), 1, 1, facecolor='lightblue',edgecolor='blue', linewidth=0.25)]

    handles = buildings_in_handle + buildings_out_handle + rivers_handle 
    labels = ['Buildings within 500m (n=' + buildings_in_no + ')', 'Buildings outside 500m (n=' + buildings_out_no + ')', 'Rivers or streams (n=' + rivers_no + ')']

    leg = ax.legend(handles, labels, title=None, title_fontsize=14, fontsize=18, loc='best', frameon=True, framealpha=1)

if __name__ == "__main__":
    db_name = 'dd_subset' # 'dd' is the complete dataset, 'dd_subset' is the subset for testing
    
    buildings_in, buildings_out, rivers = sql2gdf(db_name, password) # 1min 55 secs
    
    # Record performance profile for renderFigure() and export results to .prof file

    p = cProfile.Profile()

    p.enable()

    renderFigure(buildings_in, buildings_out, rivers)

    p.disable()

    p.dump_stats("mapcompare/profiles/" + os.path.basename(__file__)[:-3] + ' ' + '(' + db_name + ')' + ".prof")

    """
    # Visualise cProfile in browser with snakeviz
    
    profilepath = "mapcompare/profiles/" + os.path.basename(__file__)[:-3] + ' ' + '(' + db_name + ')' + ".prof"

    subprocess.run(["snakeviz", profilepath])    
    """
    
    
    # Save figure
    # plt.savefig('02_outputs/plots/' + datetime.today().strftime('%Y-%m-%d') + ' ' + db_name + '.svg', format='svg', orientation='landscape')


