

# ------------------------------------------------------------------------------
#
class Plotter(object):

    def __init__(self,style=None,plot_grid=None):
        '''
        Create a radical.analytics plot object.

        The plot is created to facilitate several types of plots for at least
        the well know data organizations that exist in radical.analytics, like
        timeseries, events, statistical plot (e.g. histograms, kernels, etc).

        The object is created by passing the following information:
        style         : The style of plot, i.e. matplotlib or bokeh #TODO
        plot_grid     : The plotting format. This is a list that keeps the
                        number of rows and columns of plots [nrows,ncols]
        '''

        self._style = style
        self._plot_grid = plot_grid

        try:
            import matplotlib.pyplot as plt
            self._plt = plt

        except:
            raise RuntimeError('Plotter class needs matplotlib installed')


    # --------------------------------------------------------------------------
    #
    def utilization(self, util_data=None, normalized=None,
                          resource=None, fig_size=None):
        '''
        This method receives as input utilization data of a specific resource
        and creates a figure for that specific utilization.

        The method is able to normalized the plot based on the owner resources
        and the utilized resources at any given time. In addition, figure's size
        can be provided as input.
        '''

        # Initially check if plot_grid is set. If not, create a single plot,
        # else create a figure based on the user's specification.
        if not self._plot_grid:

            self._fig,self._axis = self._plt.subplots(nrows=1, ncols=1,
                                                      figsize=fig_size)

            # Iterate over the owners and add a line for every owner.
            for key, util in list(util_data.items()):

                # Getting the time moments where the utilization changes
                x_axis = [point[0] for point in util['utilization']]

                # Getting the utilization points. If normalized flag is set,
                # utilization is divided with the total resources of the owner
                # and multiply with 100
                if normalized:
                    y_axis = [(point[1] / util['resources']) * 100
                                       for point in util['utilization']]
                else:
                    y_axis = [point[1] for point in util['utilization']]

                # If there is a range where the owner had the resources get it.
                # Otherwise it is none. The resource range will be use to set
                # the utilization plot correctly in the x-axis
                resource_range = util['range']
                if not resource_range:
                    resource_range = None

                if resource_range:
                    self._axis.set_xlim(resource_range)
                    self._axis.plot([resource_range[0] + x for x in x_axis],
                                    y_axis, label='%s utilization' % key)
                else:
                    self._axis.plot(x_axis,y_axis,label='%s utilization' % key)

                # X,Y label, and title are being set
                self._axis.set_ylabel('Utilization in Resources')
                self._axis.set_xlabel('Time in seconds')
                self._axis.set_title('%s Resource Utilization' % resource)
                self._axis.legend()

        else:
            self._fig,self._axis = self._plt.subplots(nrows=self._plot_grid[0],
                                                      ncols=self._plot_grid[1],
                                                      figsize=fig_size)

            # FIXME: this code is too obscure
            for (key, util),i \
                in zip(iter(list(util_data.items())), 
                   list(range(self._plot_grid[0] * self._plot_grid[1]))):

                # Getting the time moments where the utilization changes
                x_axis = [point[0] for point in util['utilization']]

                # Getting the utilization points. If normalized flag is set, utilization is
                # divided with the total resources of the owner and multiply with 100
                if normalized:
                    y_axis = [(point[1] / util['resources']) * 100 
                                       for point in util['utilization']]
                else:
                    y_axis = [point[1] for point in util['utilization']]

                # If there is a range where the owner had the resources get it. Otherwise
                # it is none. The resource range will be use to set the utilization plot
                # correctly in the x-axis
                resource_range = util['range'] if util['range'] else 0

                if resource_range:
                    self._axis[i].set_xlim(resource_range)
                    self._axis[i].plot([resource_range[0] + x for x in x_axis],
                                       y_axis, label='%s utilization' % key)
                else:
                    self._axis[i].plot(x_axis,y_axis,
                                       label='%s utilization' % key)

                # X,Y label, and title are being set
                self._axis[i].set_ylabel('Utilization in Resources')
                self._axis[i].set_xlabel('Time in seconds')
                self._axis[i].set_title('%s Resource Utilization' % resource)
                self._axis[i].legend()


    # --------------------------------------------------------------------------
    #
    def concurrency(self,data=None,fig_size=None):
        '''
        This method receives as input concurrency data and creates a figure.
        The user is able to set the figure size.
        '''

        self._fig,self._axis = self._plt.subplots(nrows=1, ncols=1,
                                                  figsize=fig_size)

        # The x axis is setup.
        x_axis = [point[0] for point in data]

        # The y axis is setup.
        y_axis = [point[1] for point in data]

        # Just plot
        self._axis.plot(x_axis,y_axis)        
        self._axis.set_ylabel('Concurrent Entities')
        self._axis.set_xlabel('Time in seconds')
        self._axis.set_title('Concurrency')


# ------------------------------------------------------------------------------

