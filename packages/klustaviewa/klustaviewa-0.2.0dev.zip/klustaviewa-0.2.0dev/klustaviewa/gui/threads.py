"""Tasks running in external threads or processes."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import time
import traceback
from threading import Lock

import numpy as np
from qtools import inthread, inprocess
from qtools import QtGui, QtCore

from klustaviewa.dataio import KlustersLoader
from klustaviewa.dataio.tools import get_array
from klustaviewa.wizard.wizard import Wizard
import klustaviewa.utils.logger as log
from klustaviewa.stats import compute_correlograms, compute_correlations


# -----------------------------------------------------------------------------
# Tasks
# -----------------------------------------------------------------------------
class OpenTask(QtCore.QObject):
    dataOpened = QtCore.pyqtSignal()
    dataSaved = QtCore.pyqtSignal()
    dataOpenFailed = QtCore.pyqtSignal(str)
        
    def open(self, loader, loader_raw, path):

        try:
            loader.close()
            loader.open(path)
            
            # now load raw data, if it exists
            loader_raw.open(path)
            
            self.dataOpened.emit()
        except Exception as e:
            self.dataOpenFailed.emit(traceback.format_exc())
            # self.dataOpenFailed.emit(e.message)

    def save(self, loader):
        loader.save()
        self.dataSaved.emit()
            

class SelectionTask(QtCore.QObject):
    selectionDone = QtCore.pyqtSignal(object, bool)
    
    def set_loader(self, loader):
        self.loader = loader
    
    def select(self, clusters, wizard):
        self.loader.select(clusters=clusters)
        
    def select_done(self, clusters, wizard, _result=None):
        self.selectionDone.emit(clusters, wizard)


class CorrelogramsTask(QtCore.QObject):
    correlogramsComputed = QtCore.pyqtSignal(np.ndarray, object, int, float)
    
    # def __init__(self, parent=None):
        # super(CorrelogramsTask, self).__init__(parent)
    
    def compute(self, spiketimes, clusters, clusters_to_update=None,
            clusters_selected=None, ncorrbins=None, corrbin=None):
        log.debug("Computing correlograms for clusters {0:s}.".format(
            str(list(clusters_to_update))))
        if len(clusters_to_update) == 0:
            return {}
        clusters_to_update = np.array(clusters_to_update, dtype=np.int32)
        correlograms = compute_correlograms(spiketimes, clusters,
            clusters_to_update=clusters_to_update,
            ncorrbins=ncorrbins, corrbin=corrbin)
        return correlograms
    
    def compute_done(self, spiketimes, clusters, clusters_to_update=None,
            clusters_selected=None, ncorrbins=None, corrbin=None, _result=None):
        correlograms = _result
        self.correlogramsComputed.emit(np.array(clusters_selected),
            correlograms, ncorrbins, corrbin)


class SimilarityMatrixTask(QtCore.QObject):
    correlationMatrixComputed = QtCore.pyqtSignal(np.ndarray, object,
        np.ndarray, np.ndarray, object)
    
    # def __init__(self, parent=None):
        # super(SimilarityMatrixTask, self).__init__(parent)
        
    def compute(self, features, clusters, 
            cluster_groups, masks, clusters_selected, target_next=None,
            similarity_measure=None):
        log.debug("Computing correlation for clusters {0:s}.".format(
            str(list(clusters_selected))))
        if len(clusters_selected) == 0:
            return {}
        correlations = compute_correlations(features, clusters, 
            masks, clusters_selected, similarity_measure=similarity_measure)
        return correlations
        
    def compute_done(self, features, clusters, 
            cluster_groups, masks, clusters_selected, target_next=None,
            similarity_measure=None, _result=None):
        correlations = _result
        self.correlationMatrixComputed.emit(np.array(clusters_selected),
            correlations, 
            get_array(clusters, copy=True), 
            get_array(cluster_groups, copy=True),
            target_next)


# -----------------------------------------------------------------------------
# Container
# -----------------------------------------------------------------------------
class ThreadedTasks(QtCore.QObject):
    def __init__(self, parent=None):
        super(ThreadedTasks, self).__init__(parent)
        self.selection_task = inthread(SelectionTask)(
            impatient=True)
        self.correlograms_task = inprocess(CorrelogramsTask)(
            impatient=True, use_master_thread=False)
        self.similarity_matrix_task = inprocess(SimilarityMatrixTask)(
            impatient=True, use_master_thread=False)

    def join(self):
        self.selection_task.join()
        self.correlograms_task.join()
        self.similarity_matrix_task.join()
        
    def terminate(self):
        self.correlograms_task.terminate()
        self.similarity_matrix_task.terminate()
    
        