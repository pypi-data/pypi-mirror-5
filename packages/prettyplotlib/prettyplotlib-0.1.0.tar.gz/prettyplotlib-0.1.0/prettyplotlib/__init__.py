#!/usr/bin/env python

import matplotlib as mpl
import matplotlib.pyplot as plt
import brewer2mpl
import numpy as np

# Get Set2 from ColorBrewer, a set of colors deemed colorblind-safe and
# pleasant to look at by Drs. Cynthia Brewer and Mark Harrower of Pennsylvania
# State University. These colors look lovely together, and are less
# saturated than those colors in Set1. For more on ColorBrewer, see:
# - Flash-based interactive map:
#     http://colorbrewer2.org/
# - A quick visual reference to every ColorBrewer scale:
#     http://bl.ocks.org/mbostock/5577023
set2 = brewer2mpl.get_map('Set2', 'qualitative', 8).mpl_colors

# Another ColorBrewer scale. This one has nice "traditional" colors like
# reds and blues
set1 = brewer2mpl.get_map('Set1', 'qualitative', 9).mpl_colors
mpl.rcParams['axes.color_cycle'] = set2

# Set some commonly used colors
almost_black = '#262626'
light_grey = np.array([float(248)/float(255)]*3)

blues = mpl.cm.Blues
blues.set_bad('white')
blues.set_under('white')

# Need to 'reverse' red to blue so that blue=cold=small numbers,
# and red=hot=large numbers with '_r' suffix
blue_red = mpl.cm.RdBu_r

# Default "patches" like scatterplots
mpl.rcParams['patch.linewidth'] = 0.75     # edge width in points

# Default empty circle with a colored outline
mpl.rcParams['patch.facecolor'] = 'none'
mpl.rcParams['patch.edgecolor'] = set2[0]

# Change the default axis colors from black to a slightly lighter black,
# and a little thinner (0.5 instead of 0.1)
mpl.rcParams['axes.edgecolor'] = almost_black
mpl.rcParams['axes.labelcolor'] = almost_black
mpl.rcParams['axes.linewidth'] = 0.5

# Make the default grid be white so it "removes" lines rather than adds
mpl.rcParams['grid.color'] = 'white'

# change the tick colors also to the almost black
mpl.rcParams['ytick.color'] = almost_black
mpl.rcParams['xtick.color'] = almost_black

# change the text colors also to the almost black
mpl.rcParams['text.color'] = almost_black

def remove_chartjunk(ax, spines, grid=None, ticklabels=None):
    '''
    Removes "chartjunk", such as extra lines of axes and tick marks.

    If grid="y" or "x", will add a white grid at the "y" or "x" axes, 
    respectively

    If ticklabels="y" or "x", or ['x', 'y'] will remove ticklabels from that
    axis
    '''
    all_spines = ['top', 'bottom', 'right', 'left']
    for spine in spines:
        ax.spines[spine].set_visible(False)

    # For the remaining spines, make their line thinner and a slightly
    # off-black dark grey
    for spine in all_spines:
        if spine not in spines:
            ax.spines[spine].set_linewidth(0.5)
            # ax.spines[spine].set_color(almost_black)
#            ax.spines[spine].set_tick_params(color=almost_black)
    # Check that the axes are not log-scale. If they are, leave the ticks
    # because otherwise people assume a linear scale.
    x_pos = set(['top', 'bottom'])
    y_pos = set(['left', 'right'])
    xy_pos = [x_pos, y_pos]
    xy_ax_names = ['xaxis', 'yaxis']

    for ax_name, pos in zip(xy_ax_names, xy_pos):
        axis = ax.__dict__[ax_name]
        # axis.set_tick_params(color=almost_black)
        if type(axis.get_scale()) == 'log':
            # if this spine is not in the list of spines to remove
            for p in pos.difference(spines):
                axis.set_ticks_position(p)
#                axis.set_tick_params(which='both', p)
        else:
            axis.set_ticks_position('none')

    if grid is not None:
        assert grid in ('x', 'y')
        ax.grid(axis=grid, color='white', linestyle='-', linewidth=0.5)
        
    if ticklabels is not None:
        assert set(ticklabels) | set(('x', 'y')) > 0
        if 'x' in ticklabels:
            ax.set_xticklabels([])
        elif 'y' in ticklabels:
            ax.set_yticklabels([])


def hist(ax, x, **kwargs):
    """
    Plots a histogram of the provided data. Can provide optional argument
    "grid='x'" or "grid='y'" to draw a white grid over the histogram. Almost like "erasing" some of the plot,
     but it adds more information!
    """
# Reassign the default colors to Set2 by Colorbrewer
    if 'color' not in kwargs:
        kwargs['color'] = set2[0]
    if 'grid' in kwargs:
        grid = kwargs['grid']
        kwargs.pop('grid')
    else:
        grid = None
    # print 'hist kwargs', kwargs
    ax.hist(x, edgecolor='white', **kwargs)
    remove_chartjunk(ax, ['top', 'right'], grid=grid)

def plot(ax, x, y, **kwargs):
    if 'color' in kwargs:
        color = kwargs['color']
        # Remove the other color argument so matplotlib doesn't complain
        kwargs.pop('color')
    else:
        # if no color is specified, cycle over the ones in this axis
        color_cycle = ax._get_lines.color_cycle
        color = color_cycle.next()

    ax.plot(x, y, color=color, **kwargs)
    remove_chartjunk(ax, ['top', 'right'])


def scatter(ax, x, y, **kwargs):
    """
    This will plot a scatterplot of x and y, iterating over the ColorBrewer
    "Set2" color cycle unless a color is specified. The symbols produced are
    empty circles, with the outline in the color specified by either 'color'
    or 'edgecolor'. If you want to fill the circle, specify 'facecolor'.
    """
    # Force 'color' to indicate the edge color, so the middle of the
    # scatter patches are empty. Can speficy
    if 'edgecolor' in kwargs:
        edgecolor = kwargs['edgecolor']
        # Remove the other color argument so matplotlib doesn't complain
        kwargs.pop('edgecolor')
    elif 'color' in kwargs:
        # Assume that color means the edge color. You can assign the
        edgecolor = kwargs['color']
        # Remove the other color argument so matplotlib doesn't complain
        kwargs.pop('color')
    else:
        # if no color is specified,
        color_cycle = ax._get_lines.color_cycle
        edgecolor = color_cycle.next()

    if 'facecolor' not in kwargs:
        kwargs['facecolor'] = 'none'

    ax.scatter(x, y, edgecolor=edgecolor, **kwargs)
    remove_chartjunk(ax, ['top', 'right'])


def bar(ax, left, height, **kwargs):
    """
    Creates a bar plot, with white outlines and a fill color that defaults to
     the first teal-ish green in ColorBrewer's Set2. Optionally accepts
     grid='y' or grid='x' to draw a white grid over the bars,
     to show the scale. Almost like "erasing" some of the plot,
     but it adds more information!
    """
    if 'color' not in kwargs:
        kwargs['color'] = set2[0]
    if 'edgecolor' not in kwargs:
        kwargs['edgecolor'] = 'white'
    if 'grid' in kwargs:
        grid = kwargs['grid']
        kwargs.pop('grid')
    else:
        grid = None
    ax.bar(left, height, **kwargs)
    remove_chartjunk(ax, ['top', 'right'], grid=grid)

def boxplot(ax, x, **kwargs):
    if 'xticklabels' in kwargs:
        xticklabels = kwargs['xticklabels']
        kwargs.pop('xticklabels')
    else:
        xticklabels = None
    bp = ax.boxplot(x, widths=0.15, **kwargs)
    if xticklabels:
        ax.xaxis.set_ticklabels(xticklabels)

    remove_chartjunk(ax, ['top', 'right', 'bottom'])

    plt.setp(bp['boxes'], color=set1[1], linewidth=0.5)
    plt.setp(bp['medians'], color=set1[0])
    plt.setp(bp['whiskers'], color=set1[1], linestyle='solid', linewidth=0.5)
    plt.setp(bp['fliers'], color=set1[1])
    plt.setp(bp['caps'], color='none')
    ax.spines['left']._linewidth = 0.5

def switch_axis_limits(ax, which_axis=('x', 'y')):
    '''
    Switch the axis limits of either x or y
    '''
    assert which_axis in ('x', 'y')
    ax_limits = ax.axis()
    if which_axis == 'x':
        ax.set_xlim(ax_limits[1], ax_limits[0])
    else:
        ax.set_ylim(ax_limits[3], ax_limits[2])

def upside_down_hist(ax, x, **kwargs):
    hist(ax, x, **kwargs)
    
    # Turn the histogram upside-down by switching the y-axis limits
    switch_axis_limits(ax, 'y')
    remove_chartjunk(ax, ['bottom', 'right'], grid='y', ticklabels='x')

def sideways_hist(ax, y, **kwargs):
    hist(ax, y, orientation='horizontal', **kwargs)
    
    # Orient the histogram with `0` counts on the right and the max
    # counts on the left by switching the `x` axis limits
    switch_axis_limits(ax, 'x')
    remove_chartjunk(ax, ['left', 'top'], grid='x', ticklabels='y')

# TODO: Heatmap-style figures. Default colormap = Blues. Check if the data
# has both negative and positive values. If so, then use blue (negative)-red
# (positive) heatmap
# def pcolor(fig, ax, x, **kwargs):
#     '''
#     Like matplotlib's pcolor, but provides a default of a
#     lightblue-to-darkblue colormap instead of a rainbow colormap. If the data
#      is detected to be both positive and negative, then will default to a
#      red-blue colormap.
#     '''
#
#     # need to check the
#     vmin = x.min()
#     vmax = x.max()
#
#     # If we have both negative and positive values, use a divergent colormap
#     if vmax > 0 and vmin < 0:
#         cmap = blue_red
#     else:
#         cmap = blues
#     p = ax.pcolor(x, cmap=cmap, vmin=vmin, vmax=vmax, **kwargs)
#     ax.set_ylim(0, x.shape[0])
#
#     remove_chartjunk(ax, ['top', 'right', 'left', 'bottom'])
#
#     # I don't think this will work because kwargs is also supplied to ax.pcolor
#     if xticklabels in kwargs:
#         xticks = np.arange(0.5, x.shape[1] + 0.5)
#         ax.set_xticks(xticks)
#         ax.set_xticklabels(xticklabels, rotation='vertical')
#     if yticklabels in kwargs:
#         yticks = np.arange(0.5, x.shape[0] + 0.5)
#         ax.set_yticks(yticks)
#         ax.set_yticklabels(yticklabels, rotation='vertical')
#
#     # Show the scale of the colorbar
#     fig.colorbar(p)


def pcolormesh(fig, ax, x, **kwargs):
    """
    Use for large datasets

    Non-traditional `pcolormesh` kwargs are:
    - xticklabels, which will put x tick labels exactly in the center of the
    heatmap block
    - yticklables, which will put y tick labels exactly aligned in the center
     of the heatmap block
     - xticklabels_rotation, which can be either 'horizontal' or 'vertical'
     depending on how you want the xticklabels rotated. The default is
     'horiztonal' but if you have xticklabels that are longer, you may want
     to do 'vertical' so they don't overlap
     - yticklabels_rotation, which can also be either 'horizontal' or
     'vertical'. The default is 'horizontal' and in most cases,
     that's what you'll want to stick with. But the option is there if you
     want.
    """
    # Deal with arguments in kwargs that should be there, or need to be taken
    #  out
    if 'vmax' not in kwargs:
        kwargs['vmax'] = x.max()
    if 'vmin' not in kwargs:
        kwargs['vmin'] = x.min()

    # If we have both negative and positive values, use a divergent colormap
    if 'cmap' not in kwargs:
        if kwargs['vmax'] > 0 and kwargs['vmin'] < 0:
            kwargs['cmap'] = blue_red
        else:
            kwargs['cmap'] = blues

    if 'xticklabels' in kwargs:
        xticklabels = kwargs['xticklabels']
        kwargs.pop('xticklabels')
    else:
        xticklabels = None
    if 'yticklabels' in kwargs:
        yticklabels = kwargs['yticklabels']
        kwargs.pop('yticklabels')
    else:
        yticklabels = None

    if 'xticklabels_rotation' in kwargs:
        xticklabels_rotation = kwargs['xticklabels_rotation']
        kwargs.pop('xticklabels_rotation')
    else:
        xticklabels_rotation = 'horizontal'
    if 'yticklabels_rotation' in kwargs:
        yticklabels_rotation = kwargs['yticklabels_rotation']
        kwargs.pop('yticklabels_rotation')
    else:
        yticklabels_rotation = 'horizontal'
    p = ax.pcolormesh(x, **kwargs)
    ax.set_ylim(0, x.shape[0])

    # Get rid of ALL axes
    remove_chartjunk(ax, ['top', 'right', 'left', 'bottom'])

    if xticklabels:
        xticks = np.arange(0.5, x.shape[1] + 0.5)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels, rotation=xticklabels_rotation)
    if yticklabels:
        yticks = np.arange(0.5, x.shape[0] + 0.5)
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels, rotation=yticklabels_rotation)
    # Show the scale of the colorbar
    fig.colorbar(p)

def legend(ax, facecolor=light_grey, **kwargs):
    legend = ax.legend(frameon=True, scatterpoints=1, **kwargs)
    rect = legend.get_frame()
    rect.set_facecolor(facecolor)
    rect.set_linewidth(0.0)

    # change the label colors in the legend to almost black
    # Change the legend label colors to almost black, too
    texts = legend.texts
    for t in texts:
        t.set_color(almost_black)

# import matplotlib.pyplot as plt
# import prettyplotlib as ppl
#
# fig, ax = plt.subplots(1)
# ppl.scatter(ax, x, y)