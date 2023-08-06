"""This module provides functions used to load probe files."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import json
import os
import tables
import time

import numpy as np
import matplotlib.pyplot as plt

from klustersloader import (find_filenames, find_index, read_xml,
    filename_to_triplet, triplet_to_filename, find_indices,
    find_hdf5_filenames,
    read_clusters, read_cluster_info, read_group_info, read_probe,)
from tools import MemMappedText, MemMappedBinary


# -----------------------------------------------------------------------------
# Probe file functions
# -----------------------------------------------------------------------------
def flatten(l):
    return sorted(set([item for sublist in l for item in sublist]))

def probe_to_json(probe_ns):
    """Convert from the old Python .probe file to the new JSON format."""
    graph = probe_ns['probes']
    shanks = sorted(graph.keys())
    if 'geometry' in probe_ns:
        geometry = probe_ns['geometry']
    else:
        geometry = None
    # Find the list of shanks.
    shank_channels = {shank: flatten(graph[shank]) for shank in shanks}
    # Find the list of channels.
    channels = flatten(shank_channels.values())
    nchannels = len(channels)
    # Create JSON dictionary.
    json_dict = {
        'nchannels': nchannels,
        'channel_names': {channel: 'ch{0:d}'.format(channel) 
            for channel in channels},
        'dead_channels': [],
        'shanks': [
                    {
                        'index': shank,
                        'channels': shank_channels[shank],
                        'graph': graph[shank],
                    }
                    for shank in shanks
                  ]
            }
    # Add the geometry if it exists.
    if geometry:
        for shank in shanks:
            for shank_dict in json_dict['shanks']:
                shank = shank_dict['index']
                # WARNING: geometry contains channels as keys, not shanks
                shank_dict['geometry'] = geometry#[shank]
    return json.dumps(json_dict)
    
def load_probe_json(probe_json):
    probe_dict = json.loads(probe_json)
    probe = {}
    probe['nchannels'] = probe_dict['nchannels']
    probe['dead_channels'] = map(int, probe_dict['dead_channels'])
    # List of all channels.
    probe['channels'] = sorted(map(int, probe_dict['channel_names'].keys()))
    # List of alive channels.
    probe['channels_alive'] = sorted(map(int, set(probe['channels']) - 
        set(probe['dead_channels'])))
    probe['nchannels_alive'] = len(probe['channels_alive'])
    # Process all shanks.
    for shank_dict in probe_dict['shanks']:
        # Find alive channels.
        shank_dict['channels_alive'] = sorted(map(int, set(shank_dict['channels']) - 
            set(probe['dead_channels'])))
        # Convert the geometry dictionary into an array.
        if 'geometry' in shank_dict:
            # Convert the keys from strings to integers.
            shank_dict['geometry'] = {int(key): val 
                for key, val in shank_dict['geometry'].iteritems()}
            # Create the geometry array with alive channels only.
            shank_dict['geometry_array'] = np.array(
                [shank_dict['geometry'][key] 
                    for key in sorted(shank_dict['geometry'].keys())
                        if key not in probe['dead_channels']], 
                dtype=np.float32)
        probe[shank_dict['index']] = shank_dict
    return probe
    

    

