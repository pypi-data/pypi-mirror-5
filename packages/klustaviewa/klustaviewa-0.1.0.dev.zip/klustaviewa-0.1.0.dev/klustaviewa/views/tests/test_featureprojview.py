"""Unit tests for feature view."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os

import numpy as np
import numpy.random as rnd
import pandas as pd

from klustaviewa.views.tests.mock_data import (setup, teardown,
                            nspikes, nclusters, nsamples, nchannels, fetdim)
from klustaviewa.dataio.loader import KlustersLoader
from klustaviewa.dataio.selection import select
from klustaviewa.dataio.tools import check_dtype, check_shape
from klustaviewa.utils.userpref import USERPREF
from klustaviewa.views import FeatureProjectionView
from klustaviewa.views.tests.utils import show_view, get_data, assert_fun


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
def test_featureprojview():
        
    keys = ('features,masks,clusters,clusters_selected,cluster_colors,'
            'fetdim,nchannels,nextrafet,duration,freq').split(',')
           
    data = get_data()
    kwargs = {k: data[k] for k in keys}
    
    kwargs['features'] = data['features_full']
    
    kwargs['operators'] = [
        lambda self: assert_fun(self.view.get_projection(0) == (0, 0)),
        lambda self: assert_fun(self.view.get_projection(1) == (0, 1)),
        lambda self: self.view.select_channel(0, 5),
        lambda self: self.view.select_feature(0, 1),
        lambda self: self.view.select_channel(1, 32),
        lambda self: self.view.select_feature(1, 2),
        lambda self: assert_fun(self.view.get_projection(0) == (5, 1)),
        lambda self: assert_fun(self.view.get_projection(1) == (32, 2)),
        
        lambda self: self.view.toggle_mask(),
        lambda self: self.view.set_wizard_pair((2, 1), (3, 2)),
        lambda self: self.view.set_wizard_pair(None, (3, 2)),
        lambda self: self.view.set_wizard_pair((3, 2), None),
        lambda self: self.view.set_wizard_pair(None, None),
        
        lambda self: self.view.set_projection(0, 2, -1),
        lambda self: self.view.set_projection(1, 2, -1),
        
        lambda self: (self.close() 
            if USERPREF['test_auto_close'] != False else None),
    ]
    
    # Show the view.
    show_view(FeatureProjectionView, **kwargs)
    
    