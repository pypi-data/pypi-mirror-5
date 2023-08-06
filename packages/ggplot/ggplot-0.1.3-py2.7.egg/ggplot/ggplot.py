import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as gradients

# ggplot stuff
from components import colors, shapes, aes
from components.legend import draw_legend
from geoms import *
from utils import *


class ggplot(object):
    """
    ggplot is the base layer or object that you use to define
    the components of your chart (x and y axis, shapes, colors, etc.).
    You can combine it with layers (or geoms) to make complex graphics
    with minimal effort.

    Parameters
    -----------
    aesthetics:  aes (ggplot.components.aes.aes)
        aesthetics of your plot
    data:  pandas DataFrame (pd.DataFrame)
        a DataFrame with the data you want to plot

    Examples
    ----------
    p = ggplot(aes(x='x', y='y'), data=diamonds)
    print p + geom_point()
    """

    # TODO: make color discrete and continuous
    CONTINUOUS = ['x', 'y', 'size']
    DISCRETE = ['color', 'shape', 'marker', 'alpha']

    def __init__(self, aesthetics, data):
        # ggplot should just 'figure out' which is which
        if not isinstance(data, pd.DataFrame):
            aesthetics, data = data, aesthetics
            
        self.aesthetics = aesthetics
        self.data = data

        # defaults
        self.geoms= []
        self.n_dim_x = 1
        self.n_dim_y = 1
        self.facets = []
        # components
        self.title = None
        self.xlab = None
        self.ylab = None
        self.legend = {}

    def __repr__(self):
        # TODO: Handle facet_wrap better so that we only have
        # as many plots as we do discrete values. Currently it
        # creates a grid of plots but doesn't use all of them
        fig, axs = plt.subplots(self.n_dim_x, self.n_dim_y)
        plt.subplot(self.n_dim_x, self.n_dim_y, 1)
        
        # Faceting just means doing an additional groupby. The
        # dimensions of the plot remain the same
        if self.facets:
            cntr = 0
            for facet, frame in self.data.groupby(self.facets):
                for layer in self._get_layers(frame):
                    for geom in self.geoms:
                        plt.subplot(self.n_dim_x, self.n_dim_y, cntr)
                        callbacks = geom.plot_layer(layer)
                        if callbacks:
                            for callback in callbacks:
                                fn = getattr(axs[cntr], callback['function'])
                                fn(*callback['args'])
                plt.title(facet)
                cntr += 1
        else:
            for layer in self._get_layers(self.data):
                for geom in self.geoms:
                    plt.subplot(1, 1, 1)
                    callbacks = geom.plot_layer(layer)
                    if callbacks:
                        for callback in callbacks:
                            fn = getattr(axs, callback['function'])
                            fn(*callback['args'])
        
        # Handling the details of the chart here; might be a better
        # way to do this...
        if self.title:
            plt.title(self.title)
        if self.xlab:
            plt.xlabel(self.xlab)
        if self.ylab:
            plt.ylabel(self.ylab)
        # TODO: Having some issues here with things that shouldn't have a legend
        # or at least shouldn't get shrunk to accomodate one. Need some sort of
        # test in place to prevent this OR prevent legend getting set to True.
        if self.legend:
            if self.facets:
                pass
                ax_to_use = [ax for ax in axs if not isinstance(ax, np.ndarray)]
                ax = axs[-1]
                box = ax.get_position()
                ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                cntr = 0
                for name, legend in self.legend.iteritems():
                    ax.add_artist(draw_legend(ax, legend, name, cntr))
                    cntr += 1
            else:
                box = axs.get_position()
                axs.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                cntr = 0
                for name, legend in self.legend.iteritems():
                    if legend:
                        axs.add_artist(draw_legend(axs, legend, name, cntr))
                        cntr += 1

        # TODO: We can probably get pretty sugary with this
        return "<ggplot: (%d)>" % self.__hash__() 

    def _get_layers(self, data=None):
        # This is handy because... (something to do w/ facets?)
        if data is None:
            data = self.data
        # We want everything to be a DataFrame. We're going to default
        # to key to handle items where the user hard codes a aesthetic
        # (i.e. alpha=0.6)
        mapping = pd.DataFrame({
            ae: data.get(key, key)
                for ae, key in self.aesthetics.iteritems()
        })
        mapping = mapping.dropna()

        # Here we're mapping discrete values to colors/shapes. For colors
        # we're also checking to see if we don't need to map them (i.e. if vars
        # are 'blue', 'green', etc.). The reverse mapping allows us to convert
        # from the colors/shapes to the original values.
        rev_color_mapping = {}
        if 'color' in mapping:
            possible_colors = np.unique(mapping.color)
            if set(possible_colors).issubset(set(colors.COLORS))==False:
                if "color" in mapping._get_numeric_data().columns:
                    # continuous
                    # TODO: add support for more colors
                    mapping['cmap'] = gradients.Blues
                else:
                    # discrete
                    color = colors.color_gen()
                    color_mapping = {value: color.next() for value in possible_colors}
                    rev_color_mapping = {v: k for k, v in color_mapping.iteritems()}
                    mapping.color = mapping.color.replace(color_mapping)

        rev_shape_mapping = {}
        if 'shape' in mapping:
            possible_shapes = np.unique(mapping['shape'])
            shape = shapes.shape_gen()
            shape_mapping = {value: shape.next() for value in possible_shapes}
            rev_shape_mapping = {v: k for k, v in shape_mapping.iteritems()}
            mapping['marker'] = mapping['shape'].replace(shape_mapping)
            del mapping['shape']

        keys = [ae for ae in self.DISCRETE if ae in mapping]
        if "cmap" in mapping:
            keys.remove("color")
        layers = []
        if len(keys)==0:
            legend = {}
            frame = mapping.to_dict('list')
            if "cmap" in frame:
                frame["cmap"] = frame["cmap"][0]
                quantiles = np.percentile(mapping.color, [0, 25, 50, 75, 100])
                # TODO: add support for more colors
                key_colors = ["white", "lightblue", "skyblue", "blue", "navy"]
                legend["color"] = dict(zip(key_colors, quantiles))
            layers.append(frame)
        else:
            legend = {"color": {}, "marker": {}}
            for name, frame in mapping.groupby(keys):
                frame = frame.to_dict('list')
                for ae in self.DISCRETE:
                    if ae in frame:
                        frame[ae] = frame[ae][0]
                        if len(keys) > 1:
                            aes_name = name[keys.index(ae)]
                        else:
                            aes_name = name
                        if ae=="color":
                            # TODO: Handle discrete vs. continuous colors here
                            # import matplotlib as mpl 
                            # cmap=mpl.cm.Blues
                            # plt.scatter(x, y, c=y, s=500, cmap=mpl.cm.gray)
                            label = rev_color_mapping.get(aes_name, aes_name)
                            legend[ae][frame[ae]] = label
                        elif ae=="shape" or ae=="marker":
                            legend[ae][frame[ae]] = rev_shape_mapping.get(aes_name, aes_name)
                            # raise Exception("Cannot have numeric shape!")
                            label = rev_shape_mapping.get(aes_name, aes_name)
                        frame['label'] = label
                if "cmap" in frame:
                    frame["cmap"] = frame["cmap"][0]
                layers.append(frame)
        # adding legends back to the plot
        # scatterpoints=1
        self.legend = legend
        return layers

