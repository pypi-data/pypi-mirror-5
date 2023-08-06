"""Raw Data View: show raw data traces."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import numpy as np

from galry import (Manager, PlotPaintManager, EventProcessor, PlotInteractionManager, Visual,
    QtGui, QtCore, NavigationEventProcessor, GridVisual, TextVisual, DataNormalizer, 
    process_coordinates, get_next_color, get_color)
from klustaviewa.views.common import KlustaViewaBindings, KlustaView
import klustaviewa.utils.logger as log
from qtools import inthread

__all__ = ['RawDataView']

# -----------------------------------------------------------------------------
# Data manager
# -----------------------------------------------------------------------------

class RawDataManager(Manager):
    info = {}
    
    # initialization
    def set_data(self, rawdata=None, freq=None, channel_height=None, channel_names=None, dead_channels=None):

        # default settings
        self.max_size = 1000
        self.duration_initial = 10.
        self.default_channel_height = 0.25
        self.channel_height_limits = (0.01, 2.)
        self.nticks = 10
        
        # these variables will be overwritten after initialization (used to check if init is complete)
        self.slice_ref = (-1, -1) # slice paging
        self.paintinitialized = False # to stop first slice from being loaded until correctly-shaped data drawn
        self.real_data = True # hides grid and painting if we've made up false data of zeros
        
        if rawdata is None:
            rawdata = np.zeros((self.duration_initial * 2, 32))
            freq = 1
            self.real_data = False
            
        # load initial variables
        self.rawdata = rawdata
        self.dead_channels = dead_channels
        self.freq = freq
        self.totalduration = (self.rawdata.shape[0] - 1) / self.freq
        self.totalsamples, self.nchannels = self.rawdata.shape
        
        if channel_height is None:
            channel_height = self.default_channel_height
        else:
            self.default_channel_height = channel_height
        self.channel_height = channel_height
        
        if channel_names is None:
            channel_names = ['ch{0:d}'.format(i) for i in xrange(self.nchannels)]
        self.channel_names = channel_names
        
        x = np.tile(np.linspace(0., self.totalduration, 2), (self.nchannels, 1))
        y = np.zeros_like(x)+ np.linspace(-1, 1, self.nchannels).reshape((-1, 1))
        
        self.position, self.shape = process_coordinates(x=x, y=y)
        
        # activate the grid
        if self.real_data == True:
            self.interaction_manager.get_processor('viewport').update_viewbox()
            self.interaction_manager.activate_grid()
        
        # register the updater threads
        self.slice_retriever = inthread(SliceRetriever)(impatient=True)
        self.slice_retriever.sliceLoaded.connect(self.slice_loaded)
        
    def load_correct_slices(self):
        
        # dirty hack to make sure that we don't redraw the window until it's been drawn once, otherwise Galry automatically rescales
        if not self.paintinitialized:
             return
        
        # dur is a paged version of the duration (using e^round(log(duration))) to avoid loading slices for every integer change in zoom level
        dur = np.exp(np.ceil(np.log(self.xlim[1] - self.xlim[0]))) 
        zoom_index = int(np.round(1 + np.log(self.duration_initial / dur)))
        index = int(np.floor(self.xlim[0] / (dur)))
        i = (index, zoom_index)
        
        if i != self.slice_ref: # we need to load a new slice
            self.slice_ref = i
            # Find needed slice(s) of data
        
            xlim_ext = self.get_buffered_viewlimits(self.xlim)
            slice = self.get_viewslice(xlim_ext)
            
            # this executes in a new thread, and calls slice_loaded when done
            self.slice_retriever.load_new_slice(self.rawdata, slice, xlim_ext, self.totalduration, self.duration_initial)
            
    def get_buffered_viewlimits(self, xlim):
        d = self.xlim[1] - self.xlim[0]
        x0_ext = np.clip(self.xlim[0] - 3 * d, 0, self.totalduration)
        x1_ext = np.clip(self.xlim[1] + 3 * d, 0, self.totalduration)
        return (x0_ext, x1_ext)
    
    def get_viewslice(self, xlim):
        d = self.xlim[1] - self.xlim[0]
        zoom = max(self.totalduration/ d, 1)
        view_size = self.totalsamples / zoom
        step = int(np.ceil(view_size / self.max_size))
        
        i0 = np.clip(int(np.round(xlim[0] * self.freq)), 0, self.totalsamples)
        i1 = np.clip(int(np.round(xlim[1] * self.freq)), 0, self.totalsamples)
        return slice(i0, i1, step)
            
    def get_undersampled_data(self, xlim, slice):
        """
        Arguments:
    
          * data: a HDF5 dataset of size Nsamples x Nchannels.
          * xlim: (x0, x1) of the desired data view.
        """
        total_size = self.rawdata.shape[0]
        
        samples = self.rawdata[slice, :]
        
        # Convert the data into floating points.
        samples = np.array(samples, dtype=np.float32)
        
        # Normalize the data.
        samples *= (1. / 65535)
        
        # Size of the slice.
        nsamples, nchannels = samples.shape
        # Create the data array for the plot visual.
        M = np.empty((nsamples * nchannels, 2))
        samples = samples.T
        M[:, 1] = samples.ravel()
        # Generate the x coordinates.
        x = np.arange(slice.start, slice.stop, slice.step) / float(total_size - 1)
        
        x = x * 2 * self.totalduration/ self.duration_initial - 1
        M[:, 0] = np.tile(x, nchannels)

        self.bounds = np.arange(nchannels + 1) * nsamples
        size = self.bounds[-1]
        return M, self.bounds, size
        
    def slice_loaded(self, samples, bounds, size):
        self.samples = samples
        self.bounds = bounds
        self.size = size
        
        colors = np.arange(self.nchannels)
        colors[self.dead_channels] = 0
        channels = np.arange(self.nchannels)
        
        self.channel_index = np.repeat(channels, self.samples.shape[0] / self.nchannels)
        self.color_index = np.repeat(colors, self.samples.shape[0] / self.nchannels)
        self.position = self.samples
        
        self.paint_manager.update_slice()
        self.paint_manager.updateGL()
        
class SliceRetriever(QtCore.QObject):
    sliceLoaded = QtCore.pyqtSignal(object, object, long)

    def __init__(self, parent=None):
        super(SliceRetriever, self).__init__(parent)
        
    def load_new_slice(self, rawdata, slice, xlim, totalduration, duration_initial):
        
        total_size = rawdata.shape[0]
        samples = rawdata[slice, :]
       
        # Convert the data into floating points.
        samples = np.array(samples, dtype=np.float32)

        # Normalize the data.
        samples *= (1. / 65535)

        # Size of the slice.
        nsamples, nchannels = samples.shape
        # Create the data array for the plot visual.
        M = np.empty((nsamples * nchannels, 2))
        samples = samples.T
        M[:, 1] = samples.ravel()
        # Generate the x coordinates.
        x = np.arange(slice.start, slice.stop, slice.step) / float(total_size - 1)

        x = x * 2 * totalduration/ duration_initial - 1
        M[:, 0] = np.tile(x, nchannels)

        bounds = np.arange(nchannels + 1) * nsamples
        size = bounds[-1]

        self.sliceLoaded.emit(M, bounds, size)

            
# -----------------------------------------------------------------------------
# Visuals
# -----------------------------------------------------------------------------
class RawDataPaintManager(PlotPaintManager):
    
    def initialize(self):
        self.add_visual(MultiChannelVisual,
            position=self.data_manager.position,
            name='rawdata_waveforms',
            shape=self.data_manager.shape,
            channel_height=self.data_manager.channel_height,
            visible=self.data_manager.real_data)

        self.add_visual(GridVisual, name='grid', background_transparent=False,
            letter_spacing=350.,)
        # if self.data_manager.no_data = False
        # self.paint_manager.set_data(visual='rawdata_waveforms', 
        #     visible=True)
        self.data_manager.paintinitialized = True

    def update(self):
        self.reinitialize_visual(visual='rawdata_waveforms',
            channel_height=self.data_manager.channel_height,
            position=self.data_manager.position,
            shape=self.data_manager.shape,
            size=self.data_manager.size,
            visible=self.data_manager.real_data)
            
        self.data_manager.paintinitialized = True
            
    def update_slice(self):
        self.set_data(visual='rawdata_waveforms',
            channel_height=self.data_manager.channel_height,
            position0=self.data_manager.position,
            shape=self.data_manager.shape,
            size=self.data_manager.size,
            channel_index=self.data_manager.channel_index,
            color_index=self.data_manager.color_index,
            bounds=self.data_manager.bounds)

class MultiChannelVisual(Visual):
    def initialize(self, color=None, point_size=1.0,
            position=None, shape=None, nprimitives=None,
            color_index=None, channel_height=None,
            options=None, autocolor=1):
        
        # register the size of the data
        self.size = np.prod(shape)
        
        # there is one plot per row
        if not nprimitives:
            nprimitives = shape[0]
            nsamples = shape[1]
        else:
            nsamples = self.size // nprimitives
        
        # register the bounds
        if nsamples <= 1:
            self.bounds = [0, self.size]
        else:
            self.bounds = np.arange(0, self.size + 1, nsamples)
        
        # automatic color with color map
        if autocolor is not None:
            if nprimitives <= 1:
                color = get_next_color(autocolor)
            else:
                color = np.array([get_next_color(i + autocolor) for i in xrange(nprimitives)])
            
        # set position attribute
        self.add_attribute("position0", ndim=2, data=position, autonormalizable=True)
    
        if color_index is None:
            color_index = np.repeat(np.arange(nprimitives), nsamples)
        color_index = np.array(color_index)
            
        # if channel_index is None:
        channel_index = np.repeat(np.arange(nprimitives), nsamples)
        channel_index = np.array(channel_index)
        
        ncolors = color.shape[0]
        ncomponents = color.shape[1]
        color = color.reshape((1, ncolors, ncomponents))
        
        dx = 1. / ncolors
        offset = dx / 2.
        
        self.add_texture('colormap', ncomponents=ncomponents, ndim=1, data=color)
        self.add_attribute('color_index', ndim=1, vartype='int', data=color_index)
        self.add_attribute('channel_index', ndim=1, vartype='int', data=channel_index)
        self.add_varying('vindex', vartype='int', ndim=1)
        self.add_uniform('nchannels', vartype='float', ndim=1, data=float(nprimitives))
        self.add_uniform('channel_height', vartype='float', ndim=1, data=channel_height)
        
        self.add_vertex_main("""
        vec2 position = position0;
        position.y = channel_height * position.y + .9 * (2 * channel_index - (nchannels - 1)) / (nchannels - 1);
        vindex = color_index;
        """)
        
        self.add_fragment_main("""
        float coord = %.5f + vindex * %.5f;
        vec4 color = texture1D(colormap, coord);
        out_color = color;
        """ % (offset, dx))
        
        # add point size uniform (when it's not specified, there might be some
        # bugs where its value is obtained from other datasets...)
        self.add_uniform("point_size", data=point_size)
        self.add_vertex_main("""gl_PointSize = point_size;""")
        

# -----------------------------------------------------------------------------
# Grid
# -----------------------------------------------------------------------------

class GridEventProcessor(EventProcessor):
    def update_axes(self, parameter):
        
        viewbox = self.interaction_manager.get_processor('viewport').viewbox
        
        text, coordinates, n = self.get_ticks_text(*viewbox)
        
        coordinates[:,0] = self.interaction_manager.get_processor('viewport').normalizer.normalize_x(coordinates[:,0])
        coordinates[:,1] = self.interaction_manager.get_processor('viewport').normalizer.normalize_y(coordinates[:,1])

        # here: coordinates contains positions centered on the static
        # xy=0 axes of the screen
        position = np.repeat(coordinates, 2, axis=0)
        position[:2 * n:2,1] = -1
        position[1:2 * n:2,1] = 1
        position[2 * n::2,0] = -1
        position[2 * n + 1::2,0] = 1

        axis = np.zeros(len(position))
        axis[2 * n:] = 1

        self.set_data(visual='grid_lines', position=position, axis=axis)

        coordinates[n:, 0] = -.95
        coordinates[:n, 1] = -.95

        t = "".join(text)
        n1 = len("".join(text[:n]))
        n2 = len("".join(text[n:]))

        axis = np.zeros(n1+n2)
        axis[n1:] = 1

        self.set_data(visual='grid_text', text=text,
            coordinates=coordinates,
            axis=axis)
            
    def nicenum(self, x, round=False):
        e = np.floor(np.log10(x))
        f = x / 10 ** e
        eps = 1e-6
        if round:
            if f < 1.5:
                nf = 1.
            elif f < 3:
                nf = 2.
            elif f < 7.:
                nf = 5.
            else:
                nf = 10.
        else:
            if f < 1 - eps:
                nf = 1.
            elif f < 2 - eps:
                nf = 2.
            elif f < 5 - eps:
                nf = 5.
            else:
                nf = 10.

        return nf * 10 ** e

    def get_ticks(self, x0, x1):
        x0 = self.interaction_manager.get_processor('viewport').normalizer.unnormalize_x(x0)
        x1 = self.interaction_manager.get_processor('viewport').normalizer.unnormalize_x(x1)
        r = self.nicenum(x1 - x0 - 1e-6, False)
        d = self.nicenum(r / (self.parent.data_manager.nticks - 1), True)
        g0 = np.floor(x0 / d) * d
        g1 = np.ceil(x1 / d) * d
        nfrac = int(max(-np.floor(np.log10(d)), 0))
        return np.arange(g0, g1 + .5 * d, d), nfrac

    def format_number(self, x, nfrac=None):
        if nfrac is None:
            nfrac = 2

        if np.abs(x) < 1e-15:
            return "0"

        # elif np.abs(x) > 1000.001:
        #     return "%.3e" % x

        # regular decimal notation (scientific notation for < 0.001s is not going to be used frequently if at all)
        return ("%." + str(nfrac) + "f") % x

    def get_ticks_text(self, x0, y0, x1, y1):
        
        ticksx, nfracx = self.get_ticks(x0, x1)
        ticksy = np.linspace(-0.9, 0.9, self.parent.data_manager.nchannels)
        
        n = len(ticksx)
        text = [self.format_number(x, nfracx) for x in ticksx]
        text += [str(self.parent.data_manager.channel_names[y]) for y in reversed(range(self.parent.data_manager.nchannels))]    
        
        # position of the ticks
        coordinates = np.zeros((len(text), 2))
        coordinates[:n, 0] = ticksx
        coordinates[n:, 1] = ticksy
        return text, coordinates, n
        
class ViewportUpdateProcessor(EventProcessor):
    def initialize(self):
        self.register('Initialize', self.update_viewport)
        self.register('Pan', self.update_viewport)
        self.register('Zoom', self.update_viewport)
        self.register('Reset', self.update_viewport)
        self.register('Animate', self.update_viewport)
        self.register(None, self.update_viewport)
    
    def update_viewbox(self):
        
        # normalization viewbox
        self.normalizer = DataNormalizer()
        self.normalizer.normalize((0, -1, self.parent.data_manager.duration_initial, 1))
            
        nav = self.get_processor('navigation')

        self.viewbox = nav.get_viewbox()
        
        nav.constrain_navigation = True
        nav.xmin = -1
        nav.xmax = 2 * (self.parent.data_manager.totalduration / self.parent.data_manager.duration_initial) - 1
        nav.sxmin = 1.
        
        self.parent.data_manager.xlim = ((self.viewbox[0] + 1) / 2. * (self.parent.data_manager.duration_initial),\
        (self.viewbox[2] + 1) / 2. * (self.parent.data_manager.duration_initial))

        # now we know the viewport has been updated, update the grid 
        self.interaction_manager.get_processor('grid').update_axes(None)
        
        # check if we need to load/unload any slices
        self.parent.data_manager.load_correct_slices()
        
    def update_viewport(self, parameter):
        self.update_viewbox()
# -----------------------------------------------------------------------------
# Interactivity
# -----------------------------------------------------------------------------
class RawDataInteractionManager(PlotInteractionManager):
    def initialize(self):
        self.register('ChangeChannelHeight', self.change_channel_height)
        self.register('Reset', self.reset_channel_height)
    
    def initialize_default(self, constrain_navigation=None,
        momentum=True,
        ):
        
        super(PlotInteractionManager, self).initialize_default()
        self.add_processor(NavigationEventProcessor,
            constrain_navigation=constrain_navigation, 
            momentum=momentum,
            name='navigation')
        
        self.add_processor(ViewportUpdateProcessor, name='viewport')
        self.add_processor(GridEventProcessor, name='grid')
        
    def activate_grid(self):
        self.paint_manager.set_data(visual='grid_lines', 
            visible=True)
        self.paint_manager.set_data(visual='grid_text',
            visible=True)
        processor = self.get_processor('grid')
        if processor:
            processor.activate(True)
            processor.update_axes(None)
            
    def change_channel_height(self, parameter):
        # get limits
        ll, ul = self.data_manager.channel_height_limits
        
        # increase/decrease channel height between limits
        if ll <= self.data_manager.channel_height <= ul:
            self.data_manager.channel_height *= (1 + parameter)
            
        # restore limits to ensure it never exceeds them
        if self.data_manager.channel_height > ul:
            self.data_manager.channel_height = ul
        elif self.data_manager.channel_height < ll:
            self.data_manager.channel_height = ll
            
        self.paint_manager.set_data(channel_height=self.data_manager.channel_height, visual='rawdata_waveforms')
        
    def reset_channel_height(self, parameter):
        self.data_manager.channel_height = self.data_manager.default_channel_height
        self.paint_manager.set_data(channel_height=self.data_manager.channel_height, visual='rawdata_waveforms')
    
class RawDataBindings(KlustaViewaBindings):      
    def initialize(self):
        self.set('Wheel', 'ChangeChannelHeight', key_modifier='Control',
                   param_getter=lambda p: p['wheel'] * .001)
# -----------------------------------------------------------------------------
# Top-level widget
# -----------------------------------------------------------------------------
class RawDataView(KlustaView):
    
    # Initialization
    # --------------
    def initialize(self):
        self.set_bindings(RawDataBindings)
        self.set_companion_classes(
            paint_manager=RawDataPaintManager,
            interaction_manager=RawDataInteractionManager,
            data_manager=RawDataManager)
    
    def set_data(self, *args, **kwargs):
        self.data_manager.set_data(*args, **kwargs)

        # update?
        if self.initialized:
            self.paint_manager.update()
            self.data_manager.load_correct_slices()
            self.updateGL()
    
    # Save and restore geometry
    # -------------------------
    def save_geometry(self):
        # pref = self.position_manager.get_geometry_preferences()
        # SETTINGS.set('rawdata_view.geometry', pref)
        pass

    def restore_geometry(self):
        """Return a dictionary with the user preferences regarding geometry
        in the WaveformView."""
        # pref = SETTINGS.get('rawdata_view.geometry')
        # self.position_manager.set_geometry_preferences(pref)
        pass

    def closeEvent(self, e):
        self.save_geometry()
        super(RawDataView, self).closeEvent(e)
      
        
