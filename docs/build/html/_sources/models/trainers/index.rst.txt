Trainers
========

The ``trainer`` module doesn't aim to replace ``brian2`` classes as much as
complement it. A trainer's goal is supervised learning of Spiking Neural
Networks. It has its own training and testing sets, as well as a backup/restore
feature that allows finishing a test run after a crash. Finally it also sends
information to a WebSocket server to be read without need of a direct access to
the program.

.. toctree::
    :caption: Available trainers

    ZengTrainer


