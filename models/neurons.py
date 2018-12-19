"""
Module regrouping all Neuron Group models.
"""
from brian2 import (Cylinder, NeuronGroup, SpatialNeuron, SpikeGeneratorGroup,
                    amp, cm, ms, msiemens, mV, ohm, uF, um, second)
from brawn.parameters import v_rest, v_threshold, v_trigger


class NeuronPrep:
    """
    NeuronGroup Preper managing the customization of Prepable objects.

    Parameters
    ----------
    Cls : class
        Class of the NeuronGroup to customize.

    Attributes
    ----------
    events : dict
        Information about the events to create.
    equations : str
        Equations of the NeuronGroup to be created.
    namespace : dict
        Namespace of the NeuronGroup to be created.

    Notes
    -----
    To simplify the process, it is recommended to use ``Prepable.customize()``
    to create a NeuronPrep and chain the customizations instead of manipulating
    this object directly.

    See Also
    --------
    Prepable

    """
    events = {
        'definitions': {},
        'codes': {},
        'scheduling': {}
    }

    def __init__(self, Cls):
        self.neuron_class = Cls
        self.equations = Cls.equations
        self.namespace = Cls.namespace

    def with_event(self, name, cond, code='', when='', order=''):
        """
        Adds an event to the customized NeuronGroup.

        Parameters
        ----------
        name : str
            Name of the event.
        condition : str
            Condition of the event firing.
        code str, optional
            Abstract code to be run when the event is fired.
        when : str, optional
            When should the event be fired.
        order : str, optional
            What order should the event be fired.

        Returns
        -------
        output : `NeuronPrep`
            Updated NeuronGroup customizer.

        """
        self.events['definitions'][name] = cond
        if code != '':
            self.events['codes'][name] = code

        self.events['scheduling'][name] = {}
        if when != '':
            self.events['scheduling'][name]['when'] = when

        if order != '':
            self.events['scheduling'][name]['order'] = order

        if self.events['scheduling'][name] == {}:
            del self.events['scheduling'][name]

        return self

    def with_constant(self, name, value):
        """
        Adds a constant to the namespace of the NeuronGroup.

        Parameters
        ----------
        name : str
            Name of the constant.
        value : `brian2.Quantity`
            Value of the constant.

        Returns
        -------
        output : `NeuronPrep`
            Updated NeuronGroup preper.
        """
        self.namespace[name] = value
        return self

    def with_variable(self, value):
        """
        Adds a variable to the equations of the NeuronGroup.

        Parameters
        ----------
        value : str
            Mathematical definition of the variable.

        Returns
        -------
        output : `NeuronPrep`
            Updated NeuronGroup preper.
        """
        self.equations += value + '\n'
        return self

    def create(self, **kwargs):
        """
        Creates the Prepable NeuronGroup using the given parameters.

        Returns
        -------
        output : ``Cls``
            NeuronGroup of the class given to the constructor.
        """
        kwargs['events'] = self.events['definitions']
        kwargs['namespace'] = self.namespace
        kwargs['equations'] = self.equations

        res = self.neuron_class(**kwargs)

        for k, v in self.events['codes'].items():
            res.run_on_event(k, v)

        for k, v in self.events['scheduling'].items():
            if 'when' in v:
                res.set_event_schedule(k, when=v['when'])
            if 'order' in v:
                res.set_event_schedule(k, order=v['order'])

        return res


class Prepable(NeuronGroup):
    """
    Abstract class for the use of NeuronPrep.

    Attributes
    ----------
    namespace : dict
        NeuronGroup namespace.
    equations : str
        NeuronGroup mathematical model.

    See Also
    --------
    NeuronPrep

    """

    namespace = {}
    equations = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def customize(cls):
        """Returns a NeuronPrep for the current class."""
        return NeuronPrep(cls)


class BasicNeuronGroup(Prepable):
    """
    Basic Leaky Integrate-and-Fire NeuronGroup.

    Parameters
    ----------
    N : int
        Number of neurons.
    name : str, optional
        Name of the NeuronGroup.
    namespace : dict, optional
        New namespace of the NeuronGroup.
    equations : str, optional
        New set of equations for the NeuronGroup.
    events : dict, optional
        Events of the NeuronGroup.

    Warnings
    --------
    Make sure all variables are accounted for if you change the namespace or
    the equations!

    """
    equations = """
dv/dt = (ge * (Ee-v_rest) + El - v) / taum : volt
dge/dt = -ge / taue : 1
"""

    namespace = {
        'taum': 10*ms,
        'Ee': 0*mV,
        'v_trigger': -53*mV,
        'v_threshold': -54*mV,
        'v_rest': -60*mV,
        'El': -74*mV,
        'taue': 5*ms
    }

    def __init__(self, N, name='neurongroup', namespace={}, equations='',
                 events={}):
        if namespace != {}:
            self.namespace = namespace

        if equations != '':
            self.equations = equations
        super().__init__(
            N=N, model=self.equations, threshold='v >= v_threshold',
            reset='v = v_rest', method='linear', name=name,
            namespace=self.namespace, events=events)

        self.v = self.namespace['v_rest']
        self.ge = 1.3


class HodgkinHuxelyNeuronGroup(Prepable):
    """
    Hodgkin-Huxely model NeuronGroup.

    Inspired by https://pdfs.semanticscholar.org/cfbf/73be5eb767fd086f43a28b472cf00b70efa8.pdf

    Parameters
    ----------
    N : int
        Number of neurons.
    name : str, optional
        Name of the NeuronGroup.
    namespace : dict, optional
        New namespace of the NeuronGroup.
    equations : str, optional
        New set of equations for the NeuronGroup.
    events : dict, optional
        Events of the NeuronGroup.

    Warnings
    --------
    Make sure all variables are accounted for if you change the namespace or
    the equations!

    """  # noqa : E501
    equations = """
dv/dt = (I_m - g_K * n**4 * (v - V_K) - g_Na * m**3 * h * (v - V_Na) - g_l * (v - V_l))/ C_m : volt

dI_m/dt = -I_m /(30*ms) : amp/metre**2
dn/dt = alphan * (1 - n) - betan * n : 1
alphan = 0.01/mV * (10*mV - v) / (exp((10*mV - v) / (10*mV)) - 1)/ms : Hz
betan = 0.125 * exp(-v / (80*mV))/ms : Hz

dm/dt = alpham * (1-m) - betam * m : 1
alpham = 0.1/mV * (25*mV - v) / (exp((25*mV - v) / (10*mV)) - 1)  /ms : Hz
betam = 4 * exp(-v / (18*mV))/ms : Hz

dh/dt = alphah * (1 - h) - betah * h : 1
alphah = 0.07 * exp( -v / (20*mV))/ms : Hz
betah = 1 / (exp((30*mV - v) / (10*mV)) + 1)/ms : Hz
"""  # noqa : E501

    namespace = {
        'C_m': 1.0 * uF / cm**2,         # Membrane capacitance

        'g_K': 36 * msiemens / cm**2,    # Maximum K channels conductance
        'V_K': -12*mV,                   # K channels threshold voltage

        'g_Na': 120 * msiemens / cm**2,  # Maximum Na channels conductance
        'V_Na': 115 * mV,                # Na channels threshold voltage

        'g_l': 0.3 * msiemens / cm**2,   # Maximum leak channels conductance
        'V_l': 10.613 * mV,              # Leak channels threshold voltage

        'v_rest': v_rest,                # Resting membrane voltage
        'v_threshold': v_threshold,      # Voltage required to trigger spike
        'v_trigger': v_trigger           # Voltage triggering spike
    }

    def __init__(self, N, name='neurongroup', namespace={}, equations='',
                 events={}):
        """
        Creates a new HodgkinHuxleyNeuronGroup.

        Parameters
        ----------
            n (int): Number of neurons.
            name (str, optional): Defaults to 'neurongroup'. Name.
            events (dict, optional): Defaults to {}. Adds specified events to
                the NeuronGroup.
        """
        if namespace != {}:
            self.namespace = namespace

        if equations != '':
            self.equations = equations

        super().__init__(N=N, model=self.equations,
                         threshold='v >= v_threshold', name=name,
                         namespace=self.namespace, refractory=25*ms,
                         method='exponential_euler', reset='v = v_rest',
                         events=events)

        # Reducing initial voltage peak to the order of e-6
        self.h = 0.59599414
        self.n = 0.3177324
        self.m = 0.05295509
        self.I_m = 0*amp/cm**2


class DocHodgkinHuxelyNeuronGroup(SpatialNeuron):
    """
    Manages a Spatial Hodgkin-Huxely model NeuronGroup.

    Inspired by https://brian2.readthedocs.io/en/stable/examples/compartmental.hh_with_spikes.html

    Attributes:
        morpho: Neuron's morphology.
        namespace: Namespace of the variables defining the Neuron.
        eqs: Equations defining the evolution of the Neuron.

    Notes:
        Inherits ModelSpatialNeuron.
    """  # noqa

    morpho = Cylinder(length=10*cm, diameter=2*238*um, n=1000, type='axon')

    namespace = {
        'El': 10.613*mV,
        'ENa': 115*mV,
        'EK': -12*mV,
        'gl': 0.3*msiemens/cm**2,
        'gNa0': 120*msiemens/cm**2,
        'gK': 36*msiemens/cm**2
    }

    # Typical equations
    eqs = """
        # The same equations for the whole neuron, but possibly different parameter values
        # distributed transmembrane current
        Im = gl * (El-v) + gNa * m**3 * h * (ENa-v) + gK * n**4 * (EK-v) : amp/meter**2
        I : amp (point current) # applied current
        dm/dt = alpham * (1-m) - betam * m : 1
        dn/dt = alphan * (1-n) - betan * n : 1
        dh/dt = alphah * (1-h) - betah * h : 1
        alpham = (0.1/mV) * (-v+25*mV) / (exp((-v+25*mV) / (10*mV)) - 1)/ms : Hz
        betam = 4 * exp(-v/(18*mV))/ms : Hz
        alphah = 0.07 * exp(-v/(20*mV))/ms : Hz
        betah = 1/(exp((-v+30*mV) / (10*mV)) + 1)/ms : Hz
        alphan = (0.01/mV) * (-v+10*mV) / (exp((-v+10*mV) / (10*mV)) - 1)/ms : Hz
        betan = 0.125*exp(-v/(80*mV))/ms : Hz
        gNa : siemens/meter**2
    """  # noqa : E501

    def __init__(self):
        """Create a new DocHodgkinHuxelyNeuronGroup."""
        super().__init__(morphology=self.morpho, model=self.eqs,
                         method="exponential_euler",
                         refractory="m > 0.4", threshold="m > 0.5",
                         Cm=1*uF/cm**2, Ri=35.4*ohm*cm,
                         namespace=self.namespace)
        self.v = 0*mV
        self.h = 1
        self.m = 0
        self.n = .5
        self.I = 0*amp  # noqa
        self.gNa = self.namespace['gNa0']


class SpikingNeuronGroup(SpikeGeneratorGroup):
    """
    Allows the use of SpikeGeneratorGroup with default spike values.

    Parameters
    ----------
    N : int
        Number of neurons.
    indices : list of int
        Neuron IDs to spike.
    times : list of `brian2.Quantity`
        Times of spiking neurons.
    name : str, optional
        Name of the NeuronGroup.

    Notes
    --------
    `Documentation of SpikeGeneratorGroup <https://brian2.readthedocs.io/en/stable/reference/brian2.input.spikegeneratorgroup.SpikeGeneratorGroup.html#brian2.input.spikegeneratorgroup.SpikeGeneratorGroup>`_.
    """ # noqa

    def __init__(self, N, indices=[], times=[]*ms,
                 period=1e100*second, name='neurongroup'):
        super().__init__(N=N, name=name, indices=indices, times=times,
                         period=period)


if __name__ == "__main__":
    print("Do not run models directly!")
