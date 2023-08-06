"""Get the keyword arguments for the views from the loader."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import numpy as np
import pandas as pd

from qtools import inthread, inprocess
from qtools import QtGui, QtCore

from klustaviewa.dataio.tools import get_array
from klustaviewa.stats.correlations import normalize
from klustaviewa.stats.correlograms import get_baselines
import klustaviewa.utils.logger as log
from klustaviewa.utils.userpref import USERPREF
from klustaviewa.utils.colors import random_color
from klustaviewa.gui.threads import ThreadedTasks


# -----------------------------------------------------------------------------
# Get data from loader for views
# -----------------------------------------------------------------------------
def get_waveformview_data(loader, autozoom=None, wizard=None):
    data = dict(
        waveforms=loader.get_waveforms(),
        clusters=loader.get_clusters(),
        cluster_colors=loader.get_cluster_colors(),
        clusters_selected=loader.get_clusters_selected(),
        masks=loader.get_masks(),
        geometrical_positions=loader.get_probe_geometry(),
        autozoom=autozoom,
        keep_order=wizard,
    )
    return data

def get_rawdataview_data(loader):
    # TODO
    # loader: HDF5RawDataLoader
    data = dict(
        raw_data=loader.get_raw_data(),
    )
    return data
    
def get_clusterview_data(loader, statscache, clusters=None):
    data = dict(
        cluster_colors=loader.get_cluster_colors('all',
            can_override=False),
        cluster_groups=loader.get_cluster_groups('all'),
        group_colors=loader.get_group_colors('all'),
        group_names=loader.get_group_names('all'),
        cluster_sizes=loader.get_cluster_sizes('all'),
        cluster_quality=statscache.cluster_quality,
    )
    return data
    
def get_correlogramsview_data(loader, statscache):
    clusters_selected = loader.get_clusters_selected()
    correlograms = statscache.correlograms.submatrix(
        clusters_selected)
    # Compute the baselines.
    sizes = get_array(loader.get_cluster_sizes())
    duration = loader.get_duration()
    corrbin = loader.corrbin
    baselines = get_baselines(sizes, duration, corrbin)
    data = dict(
        correlograms=correlograms,
        baselines=baselines,
        clusters_selected=clusters_selected,
        cluster_colors=loader.get_cluster_colors(),
        ncorrbins=loader.ncorrbins,
        corrbin=loader.corrbin,
    )
    return data
    
def get_similaritymatrixview_data(loader, statscache):
    if statscache is None:
        return
    similarity_matrix = statscache.similarity_matrix_normalized
    # Clusters in groups 0 or 1 to hide.
    cluster_groups = loader.get_cluster_groups('all')
    clusters_hidden = np.nonzero(np.in1d(cluster_groups, [0, 1]))[0]
    data = dict(
        # WARNING: copy the matrix here so that we don't modify the
        # original matrix while normalizing it.
        similarity_matrix=similarity_matrix,
        cluster_colors_full=loader.get_cluster_colors('all'),
        clusters_hidden=clusters_hidden,
    )
    return data
    
def get_featureview_data(loader, autozoom=None):
    data = dict(
        features=loader.get_features(),
        features_background=loader.get_features_background(),
        spiketimes=loader.get_spiketimes(),
        masks=loader.get_masks(),
        clusters=loader.get_clusters(),
        clusters_selected=loader.get_clusters_selected(),
        cluster_colors=loader.get_cluster_colors(),
        nchannels=loader.nchannels,
        fetdim=loader.fetdim,
        nextrafet=loader.nextrafet,
        freq=loader.freq,
        autozoom=autozoom,
        duration=loader.get_duration(),
        alpha_selected=USERPREF.get('feature_selected_alpha', .75),
        alpha_background=USERPREF.get('feature_background_alpha', .1),
        time_unit=USERPREF['features_info_time_unit'] or 'second',
    )        
    return data
    
