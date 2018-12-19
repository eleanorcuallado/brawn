"""
Module regrouping all Synapse set models.
"""

from brian2 import Synapses, ms, mV
from brawn.parameters import tau_LTP, tau_LTD, ALTP, ALTD, aLTP, aLTD, w_max


class SimpleSynapses(Synapses):
    """
    Simple pr-connecited synapses increasing current by 70 mV for each spike
    received.

    Attributes
    ----------
    namespace : dict
        Namespace of variables defining the Synapses.

    Parameters
    ----------
    input_ng : `brian2.NeuronGroup`
        Input `NeuronGroup`.
    output_ng : `brian2.NeuronGroup`
        Output `NeuronGroup`.
    name : str, optional
        Name of the synapse group.

    """

    namespace = {
        'v_incr': 70 * mV
    }

    def __init__(self, input_ng, output_ng, name='synapses'):
        super().__init__(source=input_ng, target=output_ng,
                         on_pre='v_post += v_incr',
                         namespace=self.namespace, name=name)
        self.connect()


class BasicSTDPSynapses(Synapses):
    """
    Pre-connected synapses following basic STDP behavior, with randomized
    initial weight.

    Attributes
    ----------
    equations : str
        Equations defining the evolution of the synapses.
    on_pre_eqs : str
        Equations defining the behavior on presynaptic spikes.
    on_post_eqs : str
        Equations defining the behavior on postsynaptic spikes.
    namespace : dict
        Namespace of the variables defining the synapses.

    Parameters
    ----------
    input_ng : `brian2.NeuronGroup`
        Input `NeuronGroup`.
    output_ng : `brian2.NeuronGroup`
        Output `NeuronGroup`.
    name : str, optional
        Name of the synapse group.
    """

    equations = """
        w : 1
        dApre/dt = -Apre / taupre : 1 (event-driven)
        dApost/dt = -Apost / taupost : 1 (event-driven)
    """
    on_pre_eqs = """v += w / radian * mV
        Apre += rApre
        w = clip(w + Apost, 0, gmax)
    """
    on_post_eqs = """Apost += rApost
        w = clip(w + Apre, 0, gmax)
    """

    namespace = {
        'taupre': 20*ms,
        'gmax': .05,
        'rApre': .01
    }

    def __init__(self, input_ng, output_ng, name='synapses'):
        ns = self.namespace
        ns['taupost'] = ns['taupre']
        ns['rApost'] = - ns['rApre'] * ns['taupre'] / ns['taupost'] * 1.05
        ns['rApost'] *= ns['gmax']
        ns['rApre'] *= ns['gmax']

        super().__init__(source=input_ng, target=output_ng, namespace=ns,
                         model=self.equations, on_pre=self.on_pre_eqs,
                         on_post=self.on_post_eqs, name=name)
        self.connect()
        self.w = 'rand() * gmax'


class ZengSTDPSynapses(Synapses):
    """
    Pre-connected synapses following a custom STDP protocol as described by
    Yuan Zeng (et al.) for SNN supervised learning, with randomized initial
    weight.

    Attributes
    ----------
    equations : str
        Equations defining the evolution of the synapses.
    on_pre_eqs : str
        Equations defining the behavior on presynaptic spikes.
    on_post_eqs : str
        Equations defining the behavior on postsynaptic spikes.
    namespace : dict
        Namespace of the variables defining the synapses.

    Parameters
    ----------
    input_ng : `brian2.NeuronGroup`
        Input `NeuronGroup`.
    output_ng : `brian2.NeuronGroup`
        Output `NeuronGroup`.
    name : str, optional
        Name of the synapse group.
    """

    # Custom STDP parameters
    namespace = {
        'tau_LTP': tau_LTP,  # Amplitude of decay of Potentiation learning
        'tau_LTD': tau_LTD,  # Amplitude of decay of Depression learning
        'ALTP': ALTP,  # Amplitude of trace upating for potentiation
        'ALTD': ALTD,  # Amplitude of trace updating for depression
        'aLTP': aLTP,  # Potentiation learning rate
        'aLTD': aLTD,  # Depression learning rate
        'w_max': w_max   # Max weight
    }

    equations = """
        t_prs : second   # Last registered presynaptic spike
        t_pos : second  # Last registered postsynaptic spike
        P : 1
        Q : 1
        w : 1
        val_pot : 1
        val_dep : 1
        applicable : 1
    """
    on_pre_eqs = """
        I_m = I_m + w*amp/metre**2
        t_prs = int(t_prs < 0*ms) * t + int(t_prs >= 0*ms) * t_prs
        P = P * exp((t_prs - t)/tau_LTP) + ALTP
        t_prs = t
        applicable = int(0*ms <= t_pos and t_pos < t) # Here t is a t_prs
        val_dep = applicable * aLTD * Q * exp((t_pos - t)/tau_LTD)
        w = clip(w + val_dep, 0, w_max)

    """
    on_post_eqs = """
        t_pos = int(t_pos < 0*ms) * t + int(t_pos >= 0*ms) * t_pos
        Q = Q * exp((t_pos - t)/tau_LTD) + ALTD
        t_pos = t
        applicable = int(0*ms <= t_prs and t_prs < t) # Here t is a t_post
        val_pot = applicable * aLTP * P * exp((t_prs - t)/tau_LTP)
        w = clip(w + val_pot, 0, w_max)
    """

    def __init__(self, input_ng, output_ng, name='synapses'):
        super().__init__(source=input_ng, target=output_ng,
                         model=self.equations, on_pre=self.on_pre_eqs,
                         on_post=self.on_post_eqs, namespace=self.namespace,
                         name=name)
        self.connect()
        self.t_prs = -1*ms   # If negative, no spike happened yet
        self.t_pos = -1*ms  # If negative, no spike happened yet
        self.w = 'rand() * w_max'


if __name__ == "__main__":
    print("Do not run models directly!")
