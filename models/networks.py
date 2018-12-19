"""
Module regrouping all Network models.
"""

from brian2 import (Network, StateMonitor, SpikeMonitor, EventMonitor, ms,
                    pause, figure, title, plot, xlabel, ylabel, grid, legend,
                    scatter)
from brawn.tools.data import count_spikes


class IONetwork(Network):
    """
    Two-layer network with an input NeuronGroup and an output `NeuronGroup`.

    Parameters
    ----------
    input_ng : `brian2.NeuronGroup`
        Input `NeuronGroup`.
    output_ng : `brian2.NeuronGroup`
        Output `NeuronGroup`.
    Connector : `brian2.Synapses`
        Synapses class.

    Notes
    -----
    Created ``Connector`` object is named 'synapses'.

    `IONetwork` created names begin with '__'; do not name `BrianObject`'s
    with this notation to prevent the network from modifying your
    objects without your knowledge.

    Attributes
    ----------
    input : `brian2.NeuronGroup`
        Input `NeuronGroup`.
    output : `brian2.NeuronGroup`
        Output `NeuronGroup`.

    """

    _state_monitors = {}

    _event_monitors = {}

    def __init__(self, input_ng, output_ng, Connector):
        self.input = input_ng
        self.output = output_ng
        super().__init__(self.input, self.output,
                         Connector(self.input, self.output, name='synapses'))

    def run(self, duration, record_output_spikes=False):
        """
        Runs the network for a given amount of time.

        Parameters
        ----------
        duration : `brian2.Quantity`
            Amount of time to run the network for.
        record_output_spikes : bool, optional
            Whether output spikes should be recorded.

        Returns
        -------
        output : list or None
            Spikes recorded if recording spikes, or None if not asked for.
        """
        if record_output_spikes:
            self.monitor_spikes(self.output.name, record=True,
                                name='__run_rec')

        sim_start = self.t
        super().run(duration)

        if record_output_spikes:
            trains = self['__run_rec'].spike_trains()
            self.remove(self['__run_rec'])
            return count_spikes(trains, sim_start,
                                sim_start + self.t)
        else:
            return None

    def monitor_state(self, obj, var, record=True, name=''):
        """
        Adds a `StateMonitor` to the network.

        Parameters
        ----------
        obj : str
            Name of network object to monitor.
        var : str
            Variable to monitor.
        record : bool or list of int, optional
            IDs to monitor. Records everything if True.
        name : str, optional
            Name of monitor. Defaults to '``obj`` _ ``var`` _monitor'.
        """
        mon_name = '{}_{}_monitor'.format(obj, var) if name == '' else name
        self.add(StateMonitor(self[obj], var, record=record, name=mon_name))
        self._state_monitors[mon_name] = var

    def monitor_event(self, obj, evt, record=True, name=''):
        """
        Adds an `EventMonitor` to the network.

        Parameters
        ----------
        obj : str
            Name of network oject to monitor.
        evt : str
            Event to monitor.
        record : bool or list of int, optional
            IDs to monitor. Records everything if True.
        name str, optional
            Name of monitor. Defaults to '``obj`` _ ``evt`` _monitor'.
        """
        mon_name = '{}_{}_monitor'.format(obj, evt) if name == '' else name
        self.add(EventMonitor(self[obj], evt, record=record, name=mon_name))
        self._event_monitors[mon_name] = evt

    def monitor_spikes(self, obj, record=True, name=''):
        """
        Adds a `SpikeMonitor` to the network.

        Parameters
        ----------
        obj : str
            Name of the object whose spikes to monitor.
        record : bool, optional
            IDs to monitor. Record everything if True.
        name : str, optional
            Name of monitor. Takes on '``obj`` _spike_monitor' if not
            specified.
        """
        mon_name = '{}_spike_monitor'.format(obj) if name == '' else name
        self.add(SpikeMonitor(self[obj], record=record, name=mon_name))
        self._event_monitors[mon_name] = 'spike'

    def show_state_monitor(self, monitor, window='', figure_title='',
                           name='Element {}', name_values=None, linestyle='-',
                           xlab='Time (ms)', ylab='', use_grid=True,
                           is_figure=True):
        """
        Plots a line chart for a specific `StateMonitor`.

        Parameters
        ----------
        monitor : str
            Name of the `StateMonitor`.
        window : str, optional
            Name of the window. Default value is ``monitor``.
        figure_title : str, optional
            Name of the figure.
            Default value 'Evolution of ``variable`` over time'.
        name : str, optional
            Name of each set. `{}` is replaced by the set ID.
        name_values list of str, optional
            Values replacing the set IDs for ``name``.
        linestyle : str, optional
            Line style.
        xlab : str, optional
            X-axis label.
        ylab : str, optional
            Y-axis label. Default value is '``variable`` (`dimension`)'.
        use_grid : bool, optional
            Is the grid activated?

        Warnings
        --------
        `dimension` of Volt is "m^2 kg s^-3 A^-1"!
        """
        var = self._state_monitors[monitor]
        values = getattr(self[monitor], var)

        try:
            dim = values.dim
        except AttributeError:
            dim = '1'
        if is_figure:
            figure(monitor if window == '' else window)
            title('Evolution of {} over time'.format(var)
                  if figure_title == '' else figure_title)
        i = 0
        for v in values:
            plot(self[monitor].t/ms, v, linestyle=linestyle,
                 label=(name.format(i if name_values is None
                                    else name_values[i])))
            i += 1
        xlabel(xlab)
        ylabel('{} ({})'.format(var, dim) if ylab == '' else ylab)
        if use_grid:
            grid()
        if name != '':
            legend()

    def show_event_monitor(self, monitor, window='', figure_title='',
                           xlab='Time (ms)', ylab='Neuron Index', marker='o',
                           use_grid=True, is_figure=True):
        """
        Plots a cloud chart for a specific `EventMonitor`.

        Parameters
        ----------
        monitor : str
            Name of the `EventMonitor`.
        window : str, optional
            Name of the window. Defaults to ``monitor``.
        figure_title : str, optional
            Name of the figure.
            Defaults to 'Firing of ``event`` events during simulation'.
        ylab : str, optional
            Y-axis label.
        xlab : str, optional
            X-axis label.
        marker : str, optional
            Marker style.
        use_grid : bool, optional
            Is the grid activated?
        """
        if is_figure:
            figure(monitor if window == '' else window)
            title('Firing of {} events during simulation'.format(
                    self._event_monitors[monitor])
                  if figure_title == '' else figure_title)
        scatter(self[monitor].t/ms, self[monitor].i, marker=marker)
        xlabel(xlab)
        ylabel(ylab)
        if use_grid:
            grid()

        pause(0.001)


if __name__ == "__main__":
    print("Do not run models directly!")
