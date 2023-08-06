"""This module provides utility classes and functions to load spike sorting
data sets."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import os.path
import re
from collections import Counter

import numpy as np
import pandas as pd
import tables as tb
from qtools import QtGui, QtCore

from loader import (Loader, default_group_info, reorder, renumber_clusters,
    default_cluster_info)
from klustersloader import find_filenames, save_clusters, convert_to_clu
from hdf5tools import klusters_to_hdf5
from tools import (load_text, normalize,
    load_binary, load_pickle, save_text, get_array,
    first_row, load_binary_memmap)
from probe import load_probe_json
from params import load_params_json
from auxtools import load_kwa_json, kwa_to_json, write_kwa
from selection import (select, select_pairs, get_spikes_in_clusters,
    get_some_spikes_in_clusters, get_some_spikes, get_indices, pandaize)
from kwiklib.utils.logger import (debug, info, warn, exception, FileLogger,
    register, unregister)
from kwiklib.utils.colors import COLORS_COUNT, generate_colors


# -----------------------------------------------------------------------------
# HDF5 Loader
# -----------------------------------------------------------------------------
class HDF5Loader(Loader):
    # Read functions.
    # ---------------
    def open(self, filename=None):
        """Open everything."""
        self.set_filenames(filename)
        self.open_aesthetic()
        self.open_spikes()
        self.open_traces()
        
    def set_filenames(self, filename):
        filenames = find_filenames(filename)
        self.filename_kwik = filenames['hdf5_kwik']
        self.filename_log = filenames['kvwlg']
        self.filename_clu = filenames['clu']
        self.filename_kwa = filenames['hdf5_kwa']
        self.filename_raw_kwd = filenames['hdf5_raw']
        self.filename = self.filename_kwik
        self.filenames = filenames
       
    def klusters_to_hdf5_progress_report(self, spike, nspikes, shank, nshanks):
        count = 100 * nshanks
        index = int((shank + spike * 1. / nspikes) * 100)
        self.report_progress(index, count)
       
    def open_spikes(self):
        """Open a HDF5 kwik file."""
        
        if not os.path.exists(self.filename_kwik) and os.path.exists(self.filenames['fet']):
            klusters_to_hdf5(self.filename, self.klusters_to_hdf5_progress_report)
        
        self.initialize_logfile()
        # Load the similarity measure chosen by the user in the preferences
        # file: 'gaussian' or 'kl'.
        # Refresh the preferences file when a new file is opened.
        # USERPREF.refresh()
        self.similarity_measure = self.userpref['similarity_measure'] or 'gaussian'
        debug("Similarity measure: {0:s}.".format(self.similarity_measure))
        info("Opening {0:s}.".format(self.filename))
            
        if os.path.exists(self.filename):
            self.kwik = tb.openFile(self.filename, mode='r+')
            # Get the list of shanks.
            # WARNING
            # The commented code above detects the shank indices from introspection
            # in the "shanks" group. It is not necessary anymore as soon as the
            # metadata contains a "SHANKS" attribute with the list of shanks.
            # self.shanks = [int(re.match("shank([0-9]+)", 
                # shank._v_name).group(1)[0])
                    # for shank in self.kwik.listNodes('/shanks')]
            self.read_metadata(self.kwik)
            # By default, read the first available shank.
            self.set_shank(self.shanks[0])
            self.read_shank()
        
    def open_aesthetic(self):
        # Read KWA file.
        try:
            with open(self.filename_kwa) as f:
                self.kwa_json = f.read()
            self.kwa = load_kwa_json(self.kwa_json)
        except IOError:
            self.kwa_json = None
            self.kwa = {}
    
    def open_traces(self):
        try:
            self.kwd_raw = tb.openFile(self.filename_raw_kwd)
            self.read_metadata(self.kwd_raw)
            self.set_shank(self.shanks[0])
            self.read_nchannels()
            self.read_kwa_channels()
        except:
            self.kwd_raw = None
    
    # Shank functions.
    # ----------------
    def get_shanks(self):
        """Return the list of shanks available in the file."""
        return self.shanks
        
    def set_shank(self, shank):
        """Change the current shank and read the corresponding tables."""
        if not shank in self.shanks:
            warn("Shank {0:d} is not in the list of shanks: {1:s}".format(
                shank, str(self.shanks)))
        self.shank = shank
        self.shank_path = '/shanks/shank{0:d}'.format(self.shank)
    
    def read_shank(self, shank=None):
        """Read the tables corresponding to a given shank."""
        if shank is not None:
            self.shank = shank
        # Get the tables.
        self.spike_table = self.kwik.getNode(
            self.shank_path + '/spikes')
        self.wave_table = self.kwik.getNode(
            self.shank_path + '/waveforms')
        self.clusters_table = self.kwik.getNode(
            self.shank_path + '/clusters')
        self.groups_table = self.kwik.getNode(
            self.shank_path + '/groups_of_clusters')
        # Get the contents.
        self.read_nchannels()
        self.read_fetdim()
        self.read_nsamples()
        self.read_clusters()
        self.read_spiketimes()
        self.read_kwa_clusters()
        self.read_arrays()
        
    
    # Read contents.
    # --------------
    def read_metadata(self, datafile):
        """Read the metadata in /metadata."""
        params_json = datafile.getNodeAttr('/metadata', 'PRM_JSON') or None
        self.params = load_params_json(params_json)
        
        # Read the sampling frequency.
        self.freq = self.params['freq']
        
        # Read the number of features, global or per-shank information.
        try:
            self.fetdim = int(self.params['fetdim'])
        except:
            # To be set in "set_shank" as it is per-shank information.
            self.fetdim = None
            
        # Read the number of samples, global or per-shank information.
        try:
            self.nsamples = int(self.params['nsamples'])
        except:
            # To be set in "set_shank" as it is per-shank information.
            self.nsamples = None
        
        probe_json = datafile.getNodeAttr('/metadata', 'PRB_JSON') or None
        self.shanks = list(datafile.getNodeAttr('/metadata', 'SHANKS'))
        self.probe = load_probe_json(probe_json)

    def read_nchannels(self):
        """Read the number of alive channels from the probe file."""
        channels = self.probe[self.shank]['channels']
        channels_ignored = self.params['ignored_channels']
        channels_alive = sorted(set(channels) - set(channels_ignored))
        self.nchannels = len(channels_alive)
        
    def read_fetdim(self):
        if self.fetdim is None:
            self.fetdim = self.params['fetdim'][self.shank]
        
    def read_nsamples(self):
        if self.nsamples is None:
            self.nsamples = self.params['nsamples'][self.shank]
        
    def get_probe_geometry(self):
        if self.probe:
            return self.probe[self.shank].get('geometry_array', None)
        else:
            return None
        
    def read_clusters(self):
        clusters = self.spike_table.col('cluster_manual')
        self.nspikes = clusters.shape[0]
        # Convert to Pandas.
        self.clusters = pd.Series(clusters, dtype=np.int32)
        # Count clusters.
        self._update_data()
    
    def read_spiketimes(self):
        spiketimes = self.spike_table.col('time') * (1. / self.freq)
        # Convert to Pandas.
        self.spiketimes = pd.Series(spiketimes, dtype=np.float32)
        self.duration = spiketimes[-1]
    
    def read_kwa_clusters(self):
        # Read KWA JSON string.
        # Read the cluster info.
        clusters = self.clusters_table.col('cluster')
        cluster_groups = self.clusters_table.col('group')
        
        groups = self.groups_table.col('group')
        group_names = self.groups_table.col('name')

        # Getting the colors from the KWA file, or creating them.
        # kwa = load_kwa_json(self.kwa_json)
        if self.kwa:
            cluster_colors = self.kwa['shanks'][self.shank]['cluster_colors']
            group_colors = self.kwa['shanks'][self.shank]['group_colors']
        else:
            cluster_colors = generate_colors(len(clusters))
            group_colors = generate_colors(len(groups))
         
        # Create the cluster_info DataFrame.
        self.cluster_info = pd.DataFrame(dict(
            color=cluster_colors,
            group=cluster_groups,
            ), index=clusters)
        self.cluster_colors = self.cluster_info['color'].astype(np.int32)
        self.cluster_groups = self.cluster_info['group'].astype(np.int32)

        # Create the group_info DataFrame.
        self.group_info = pd.DataFrame(dict(
            color=group_colors,
            name=group_names,
            ), index=groups)
        self.group_colors = self.group_info['color'].astype(np.int32)
        self.group_names = self.group_info['name']
         
         
    def read_kwa_channels(self):
        # create channel attributes
        # channel_names, channel_colors, channel_groups, channel_group_names, channel_group_colors, channels_visible, channel_groups_visible
        if self.kwa.get('channels', {}):
            channels = sorted(self.kwa['channels'].keys())
            self.channel_colors = pd.Series([self.kwa['channels'][channel]['color'] for channel in channels], index=channels)
            self.channel_names = pd.Series([self.kwa['channels'][channel]['name'] for channel in channels], index=channels)
            self.channel_groups = pd.Series([self.kwa['channels'][channel]['group'] for channel in channels], index=channels)
            self.channels_visible = pd.Series([self.kwa['channels'][channel]['visible'] for channel in channels], index=channels)
        else:
            self.channel_names = pd.Series(["ch{0:d}".format(channel) for channel in xrange(self.nchannels)])
            self.channel_colors = pd.Series(np.mod(np.arange(self.nchannels, dtype=np.int32), COLORS_COUNT) + 1)
            
            # TODO: put channels in shanks rather than assuming they're all in group 0
            self.channel_groups = pd.Series(np.zeros(self.nchannels))
        
        if self.kwa.get('groups_of_channels', {}):
            channel_groups = sorted(self.kwa['groups_of_channels'].keys())
            self.channel_group_colors = pd.Series([self.kwa['groups_of_channels'][group]['color'] for group in channel_groups], index=channel_groups)
            self.channel_group_names = pd.Series([self.kwa['groups_of_channels'][group]['name'] for group in channel_groups], index=channel_groups)
            self.channel_groups_visible = pd.Series([self.kwa['groups_of_channels'][group]['visible'] for group in channel_groups], index=channel_groups)
        else:
            
            # TODO: put channels in shanks rather than assuming they're all in group 0
            self.channel_group_names = pd.Series(["Group 1"])
            self.channel_group_colors = pd.Series([0])
    
    # Read and process arrays.
    # ------------------------
    def process_features(self, y):
        x = y.copy()
        # Normalize all regular features.
        x[:,:x.shape[1]-self.nextrafet] *= self.background_features_normalization
        # Normalize extra features except time.
        if self.nextrafet > 1:
            x[:,-self.nextrafet:-1] *= self.background_extra_features_normalization
        # Normalize time.
        x[:,-1] *= (1. / (self.duration * self.freq))
        x[:,-1] = 2 * x[:,-1] - 1
        return x
    
    def process_masks_full(self, masks_full):
        return (masks_full * 1. / 255).astype(np.float32)
    
    def process_masks(self, masks_full):
        return (masks_full[:,:-self.nextrafet:self.fetdim] * 1. / 255).astype(np.float32)
    
    def process_waveforms(self, waveforms):
        return (waveforms * 1e-5).astype(np.float32).reshape((-1, self.nsamples, self.nchannels))
    
    def read_arrays(self):
        self.nextrafet = (self.spike_table.cols.features.shape[1] - 
            self.nchannels * self.fetdim)
            
        self.features = self.spike_table, 'features', self.process_features
        self.masks_full = self.spike_table, 'masks', self.process_masks_full
        self.masks = self.spike_table, 'masks', self.process_masks
        self.waveforms = self.wave_table, 'waveform', self.process_waveforms
        
        # Background spikes
        # -----------------
        # Used for:
        #   * background feature view
        #   * similarity matrix
        # Load background spikes for FeatureView.
        step = max(1, int(self.nspikes / (1000. * self.nclusters)))
        self.background_spikes = slice(0, self.nspikes, step)
        self.background_table = self.spike_table[self.background_spikes]
        self.background_features = self.background_table['features']
        # Find normalization factor for features.
        ncols = self.background_features.shape[1]
        self.background_features_normalization = 1. / np.abs(
            self.background_features[:,:ncols-self.nextrafet]).max()
        # Normalize extra features except time.
        if self.nextrafet > 1:
            self.background_extra_features_normalization = 1. / (np.median(np.abs(
                self.background_features[:,-self.nextrafet:-1])) * 2)
        self.background_features = self.process_features(
            self.background_features)
        # self.background_features_pandas = pandaize(
            # self.background_features, self.background_spikes)
        self.background_masks = self.process_masks_full(
            self.background_table['masks'])
        self.background_clusters = self.background_table['cluster_manual']
        self.spikes_selected_table = None
        
    # Raw data functions.
    def get_trace(self):
        try:
            trace = self.kwd_raw.root.data
        except:
            trace = None
            
        if trace != None:
            freq = self.params['freq']
            ignored_channels = self.params['ignored_channels']
            channel_colors = self.channel_colors
            channel_names = self.channel_names
        else:
            freq = ignored_channels = channel_colors = channel_names = None
            
        data = dict(
            trace=trace,
            freq=freq,
            ignored_channels=ignored_channels,
            channel_colors=channel_colors,
            channel_names=channel_names
        )
        return data

    # Access to the data: spikes
    # --------------------------
    def select(self, spikes=None, clusters=None):
        if clusters is not None:
            if not hasattr(clusters, '__len__'):
                clusters = [clusters]
            spikes = get_spikes_in_clusters(clusters, self.clusters)
        # HDD access here: get the portion of the table with the requested 
        # clusters (cache). It is very quick to access the different columns
        # from this in-memory table later.
        if spikes is not None:
            self.spikes_selected_table = self.spike_table[spikes]
            # Select waveforms too.
            self.spikes_waveforms = get_some_spikes_in_clusters(clusters, self.clusters,
                    counter=self.counter,
                    nspikes_max_expected=self.userpref['waveforms_nspikes_max_expected'],
                    nspikes_per_cluster_min=self.userpref['waveforms_nspikes_per_cluster_min'])
            self.waveforms_selected = self.waveforms[0][self.spikes_waveforms]['waveform_filtered']
        else:
            self.spikes_selected_table = None
            self.waveforms_selected = None
        self.spikes_selected = spikes
        self.clusters_selected = clusters

    def get_features_background(self):
        # return self.background_features_pandas
        return pandaize(self.background_features, self.background_spikes)
    
    def get_features(self, spikes=None, clusters=None):
        if self.spikes_selected_table is None:
            return None
        # Special case: return the already-selected values from the cache.
        if spikes is None and clusters is None:
            features = self.spikes_selected_table['features']
            values = self.process_features(features)
            return pandaize(values, self.spikes_selected)
        # Normal case.
        if clusters is not None:
            spikes = get_spikes_in_clusters(clusters, self.clusters)
        if spikes is None:
            spikes = self.spikes_selected
        return select(self.features, spikes)
    
    def get_masks(self, spikes=None, full=None, clusters=None):
        if self.spikes_selected_table is None:
            return None
        # Special case: return the already-selected values from the cache.
        if spikes is None and clusters is None:
            masks = self.spikes_selected_table['masks']
            if full:
                values = self.process_masks_full(masks)
            else:
                values = self.process_masks(masks)
            return pandaize(values, self.spikes_selected)
            
        # Normal case.
        if clusters is not None:
            spikes = get_spikes_in_clusters(clusters, self.clusters)
        if spikes is None:
            spikes = self.spikes_selected
        if not full:
            masks = self.masks
        else:
            masks = self.masks_full
        return select(masks, spikes)
    
    def get_waveforms(self, spikes=None, clusters=None):
        
        if self.waveforms_selected is None:
            return None
        # Special case: return the already-selected values from the cache.
        if spikes is None and clusters is None:
            values = self.process_waveforms(self.waveforms_selected)
            return pandaize(values, self.spikes_waveforms)
        
        # Normal case.
        if self.spikes_selected_table is None:
            return None
        if spikes is not None:
            return select(self.waveforms, spikes)
        else:
            if clusters is None:
                clusters = self.clusters_selected
            if clusters is not None:
                spikes = get_some_spikes_in_clusters(clusters, self.clusters,
                    counter=self.counter,
                    nspikes_max_expected=self.userpref['waveforms_nspikes_max_expected'],
                    nspikes_per_cluster_min=self.userpref['waveforms_nspikes_per_cluster_min'])
            else:
                spikes = self.spikes_selected
        return select(self.waveforms, spikes)
    
    
    # Log file.
    # ---------
    def initialize_logfile(self):
        self.logfile = FileLogger(self.filename_log, name='datafile', 
            level=self.userpref['loglevel_file'])
        # Register log file.
        register(self.logfile)
        
    
    # Save.
    # -----
    def _update_table_size(self, table, size_new, default=None):
        if default is None:
            cols = table.colnames
            dtype = [(name, table.coldtypes[name]) for name in cols]
            default = np.zeros(1, dtype=dtype)
        nrows_old = table.nrows
        if size_new < nrows_old:
            table.removeRows(0, nrows_old - size_new)
        elif size_new > nrows_old:
            for _ in xrange(size_new - nrows_old):
                table.append(default)
    
    def save(self, renumber=False):
        
        # Report progress.
        self.report_progress_save(1, 6)
        
        self.update_cluster_info()
        self.update_group_info()
        
        # Renumber internal variables, knowing that in this case the file
        # will be automatically reloaded right afterwards.
        if renumber:
            self.renumber()
            self.clusters = self.clusters_renumbered
            self.cluster_info = self.cluster_info_renumbered
            self._update_data()
        
        # Update the changes in the HDF5 tables.
        self.spike_table.cols.cluster_manual[:] = get_array(self.clusters)
        
        
        # Report progress.
        self.report_progress_save(2, 6)
        
        # Update the clusters table.
        # --------------------------
        # Add/remove rows to match the new number of clusters.
        self._update_table_size(self.clusters_table, 
            len(self.get_clusters_unique()))
        self.clusters_table.cols.cluster[:] = self.get_clusters_unique()
        self.clusters_table.cols.group[:] = self.cluster_info['group']
        
        
        # Report progress.
        self.report_progress_save(3, 6)
        
        # Update the group table.
        # -----------------------
        # Add/remove rows to match the new number of clusters.
        groups = get_array(get_indices(self.group_info))
        self._update_table_size(
            self.groups_table, 
            len(groups), )
        self.groups_table.cols.group[:] = groups
        self.groups_table.cols.name[:] = self.group_info['name']
        
        # Commit the changes on disk.
        self.kwik.flush()
        
        
        # Report progress.
        self.report_progress_save(4, 6)
        
        # Save the CLU file.
        # ------------------
        save_clusters(self.filename_clu, 
            convert_to_clu(self.clusters, self.cluster_info['group']))
        
        
        # Report progress.
        self.report_progress_save(5, 6)
        
        # Update the KWA file.
        # --------------------
        kwa={}
        kwa['shanks'] = {
            shank: dict(
                cluster_colors=self.cluster_info['color'],
                group_colors=self.group_info['color'],
            ) for shank in self.shanks
        }
        write_kwa(self.filename_kwa, kwa)
        
        # Report progress.
        self.report_progress_save(6, 6)
    
    
    # Close functions.
    # ----------------
    def close(self):
        """Close the kwik HDF5 file."""
        if hasattr(self, 'kwik') and self.kwik.isopen:
            self.kwik.flush()
            self.kwik.close()
        if hasattr(self, 'logfile'):
            unregister(self.logfile)
       
        