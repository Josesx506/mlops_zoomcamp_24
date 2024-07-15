import os
from datetime import datetime,timedelta
from functools import lru_cache, wraps

import osmnx as ox
from osmnx import graph_from_place, graph_from_point, save_graphml
from pkg.model.utils import get_data_dir

ox.settings.log_console=True

def timed_lru_cache(seconds: int, maxsize: int = None, verbose=False):
    """
    Author: https://www.mybluelinux.com/pyhon-lru-cache-with-time-expiration/
    """
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.now() + func.lifetime
        func.verbose = verbose
        
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if func.verbose:
                print(f"Current Time: {datetime.now()}, Cache expiration: {func.expiration}")
            if datetime.now() >= func.expiration:
                if func.verbose:
                    print("Cache lifetime expired, retrieving data")
                func.cache_clear()
                func.expiration = datetime.now() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache

def create_nyc_graphml(mode="drive",cent_coords=(40.723782,-73.98031),
               place="New York City, New York, United States",radius_m=50000):
    """
    Download the open street map driving network data for 50 km around a 
    center point in NYC.

    Saves a compressed zipped `graphml.gz` file in the data folder.
    """
    graph = graph_from_point(cent_coords, dist=radius_m, network_type=mode)
    filename = f"{get_data_dir()}/nyc-taxi-osm.graphml.gz"
    save_graphml(graph, filename, gephi=False)
    return None

@timed_lru_cache(7200)
def load_nyc_graphml():
    """
    Load the saved graphml file. If it's not available, download it
    Returns:
        ox.graphml: NYC driving network data
    """
    filename = f"{get_data_dir()}/nyc-taxi-osm.graphml.gz"
    if os.path.isfile(filename):
        graph = ox.load_graphml(filename)
    else:
        create_nyc_graphml()
        graph = ox.load_graphml(filename)
    return graph