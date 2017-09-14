import matplotlib.pyplot as plt

class Plotter(object):

    def __init__(self,style=None,plot_grid=None):
        """
        Create a radical.analytics plot object.

        The plot is created to facilitate several types of plots for at least the
        well know data organizations that exist in radical.analytics, like timeseries,
        events, statistical plot (e.g. histograms, kernels, etc).

        The object is created by passing the following information:
        style         : The style of plot, i.e. matplotlib or bokeh #TODO
        plot_grid     : The plotting format. This is a list that keeps the number of rows
                        and columns of plots [nrows,ncols]


        """

        self._style = style
        self._plot_grid = plot_grid
        
    def utilization(self,util_data=None,normalized=None,resource=None):
        
        if not self._plot_grid:
            self._fig,self._axis = plt.subplots(nrows=1,ncols=1)
            for key, util in util_data.iteritems():
                x_axis = [point[0] for point in util['utilization']]
                if normalized:
                    y_axis = [(point[1]/util['resources'])*100 for point in util['utilization']]
                else:
                    y_axis = [point[1] for point in util['utilization']]
                resource_range = util['range'] if util['range'] else 0
                
                if resource_range:
                    self._axis.set_xlim(resource_range)
                    self._axis.plot([resource_range[0]+x for x in x_axis],y_axis,label='%s utilization'%key)
                else:
                    self._axis.plot(x_axis,y_axis,label='%s utilization'%key)
                
                self._axis.set_ylabel('Utilization in Resources')
                self._axis.set_xlabel('Time in seconds')
                self._axis.set_title('%s Resource Utilization'%resource)
                self._axis.legend()

        else:
            self._fig,self._axis = plt.subplots(nrows=self._plot_grid[0],ncols=self._plot_grid[1])
            for (key, util),i in zip(util_data.iteritems(),range(self._plot_grid[0]*self._plot_grid[1])):
                x_axis = [point[0] for point in util['utilization']]
                if normalized:
                    y_axis = [(point[1]/util['resources'])*100 for point in util['utilization']]
                else:
                    y_axis = [point[1] for point in util['utilization']]
                resource_range = util['range'] if util['range'] else 0
                
                if resource_range:
                    self._axis[i].set_xlim(resource_range)
                    self._axis[i].plot([resource_range[0]+x for x in x_axis],y_axis,label='%s utilization'%key)
                else:
                    self._axis[i].plot(x_axis,y_axis,label='%s utilization'%key)
            
                self._axis[i].set_ylabel('Utilization in Resources')
                self._axis[i].set_xlabel('Time in seconds')
                self._axis[i].set_title('%s Resource Utilization'%resource)
                self._axis[i].legend()

    def concurrency(self,data=None):
        
        self._fig,self._axis = plt.subplots(nrows=1,ncols=1)
        x_axis = [point[0] for point in data]
        y_axis = [point[1] for point in data]
        self._axis.plot(x_axis,y_axis)        
        self._axis.set_ylabel('Concurrent Entities')
        self._axis.set_xlabel('Time in seconds')
        self._axis.set_title('Concurrency')

