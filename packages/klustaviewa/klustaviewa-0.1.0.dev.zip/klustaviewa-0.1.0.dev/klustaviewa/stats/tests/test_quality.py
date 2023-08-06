"""Unit tests for stats.quality module."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os

import numpy as np

from klustaviewa.dataio.tests.mock_data import (setup, teardown,
                            nspikes, nclusters, nsamples, nchannels, fetdim)
from klustaviewa.dataio.loader import KlustersLoader
from klustaviewa.stats.quality import cluster_quality

                            
# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------
def load():
    # Open the mock data.
    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                '../../dataio/tests/mockdata')
    xmlfile = os.path.join(dir, 'test.xml')
    l = KlustersLoader(filename=xmlfile)
    # c = Controller(l)
    return l


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
def test_quality():
    l = load()
    
    clusters_selected = [2, 3, 5]
    l.select(clusters=clusters_selected)
    waveforms = l.get_waveforms()
    features = l.get_features()
    masks = l.get_masks(full=True)
    clusters = l.get_clusters()
    
    quality = cluster_quality(waveforms, features, clusters, masks, 
        clusters_selected)
    
    l.close()
    