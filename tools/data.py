"""
Module regrouping various tools to process network spike informations.
"""


def count_spikes(spike_train, start, end):
    """
    Returns the number of spikes per neuron in a time interval.

    Parameters
    ----------
    spike_train: dict
        Spike train to analyze.
    start: `brian2.Quantity`
        Beginning of period to analyze.
    end: `brian2.Quantity
        End of period to analyze.

    Returns
    -------
    class_spikes : list of int
        Number of spikes per neuron.
    """
    return list(map(
        lambda i:
            len(list(filter(
                lambda val:
                    end > val >= start,
                spike_train[i]))),
        spike_train))


def get_class_spike_number(spikes, class_size, class_amount):
    """
    Returns the number of spiking neurons per class.

    Parameters
    ----------
    spikes: list of int
        Number of spikes per neuron.
    class_size: int
        Number of neurons per class.
    class_amount: int
        Number of classes.

    Returnss
    -------
    spike_amounts: list of int
        Number of spiking neurons per class.
    """
    numbers = []
    for class_id in range(class_amount):
        spiking = 0
        for i in range(class_size):
            if spikes[class_id * class_size + i] > 0:
                spiking += 1
        numbers.append(spiking)

    return numbers


def get_class_spike_ids(spikes, class_size, class_amount):
    """
    Returns a list of spiking and non-spiking neurons per each class.

    Parameters
    ----------
    spikes: list of int
        Number of spikes per neuron.
    class_size: int
        Number of neurons per class.
    class_amount: int
        Number of classes.

    Returns
    -------
    spiking: list of int
        Array of spiking neuron IDs per class.
    non_spiking: list of int
        Array of non-spiking neuron IDs per class.
    """
    spiking = []
    non_spiking = []
    for class_id in range(class_amount):
        spiking.append([])
        non_spiking.append([])
        for i in range(class_size):
            member_id = class_id * class_size + i
            if spikes[member_id] > 0:
                spiking[class_id].append(member_id)
            else:
                non_spiking[class_id].append(member_id)
    return spiking, non_spiking
