#####
Brawn
#####
--------------------------
A simplified use of Brian2
--------------------------
Brian2 is a rather complex library with very powerful options, but it can seem
a little overwhelming at the beginning, and though it may be simple to do for
small things, its syntax means that the code can rapidly be pretty long
syntaxically with very little high-level operations being done. Thankfully,
**brawn** is here to do the heavylifting. The goal of this library is to
simplify the use of the more common functions in Brian2 to make it syntaxically
simpler to make higher-level operations clearer in the python code.

**This library gives you the brain & the brawn to manipulate Spiking Neural
Networks!**

The main part of the code is in the `models` module. This module contains the
**brawn** models for neurons, synapses, networks and trainers. Those models are
here to replace Brian2's native elements of the same name.

The `tools` module is a repository of packages with functions used throughout
the project. Added to this is the `parameters.py` file, which is a set of
variables that are used throughout the roject and that allow easy modification
to the codebase. They tend to be problem specific, and it is recommended to add
other potential reused variables to it, to allow easy modifications to those.

Warning: It is recommended that you have already completed the `brian2
tutorials`_ before reading this documentation!

Note that this library is meant to be expanded! The best way to use it is to
create new models that you may need in your project using the available tools.
The project contains two examples - the :ref:`zeng-stdp-synapses` and
:ref:`zeng-trainer` - that are problem-specific. These classes exist to give
you an idea of how to use the library to create your own problem-specific
classes.

Don't hesitate to contact me for questions or bugs by email:
`kevin.cuallado@gmail.com`_

Contents:

.. toctree::
    :maxdepth: 4

    models/index
    tools/index
    websocket

.. _kevin.cuallado@gmail.com: mailto:kevin.cuallado@gmail.com
.. _brian2 tutorials: https://brian2.readthedocs.io/en/stable/resources/tutorials/index.html
