Neurons
=======

The ``neurons`` model replaces the ``brian2.NeuronGroup`` objects. The module
contains *preset* classes whose information (equations, triggers, rest... etc.)
have already been filled out. The classes inheriting the :ref:`prepable` allow
for the use of the ``.customize()``, which helps customizing the created
objects. When using that function, you can then chain functions
``.with_event()``, ``.with_variable()`` and ``.with_constant()`` which add a
new event, a new variable in the equations and a new element in the namespace,
respectively ; you can then finish with the ``.create()`` using the usual
constructor arguments to get a the customized object. Here's an example of a
custom object::

    from models.neurons import BasicNeuronGroup
    custom_ng = BasicNeuronGroup.customize().with_constant(
        'cstA', '35*mV').with_variable('varA = v + cstA').with_event(
        name='evtA', cond='varA > 50*mV', code='v = 0*mV', when='start', order=3
    ).create(N=3, name='custom_ng')

.. toctree::
    :caption: Available neurons

    NeuronPrep
    Prepable
    BasicNeuronGroup
    HodgkinHuxelyNeuronGroup
    SpikingNeuronGroup
