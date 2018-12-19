"""
Module with classes aiming at training SNNs.

Contains:
    ZengTrainer: Supervised learning SNN trainer for character recognition.
"""
import logging
import os
import pickle
import random as rng
from asyncio import get_event_loop
from json import dumps, loads

from brian2 import ms
from tqdm import tqdm
from websockets import connect

from brawn.models.networks import IONetwork
from brawn.models.neurons import SpikingNeuronGroup as InputClass
from brawn.parameters import (ALTD, ALTP, T01, T02, T03, T10, T11, T12, T13,
                              active_threshold, aLTD, aLTP, class_amount,
                              class_size, cycle_time, inactive_threshold,
                              progress_monitoring, tau_LTD, tau_LTP,
                              test_data_size, train_data_size, train_step,
                              train_time, v_rest, v_threshold, v_trigger,
                              w_max, websocket_logging)
from brawn.tools.data import get_class_spike_ids, get_class_spike_number
from brawn.tools.image import image2spikes

# --- Constants ---- #
FIRST = 0


class ZengTrainer:
    """
    Object training SNNs according to the protocol by Zeng et al with no
    NetworkOperation.

    Attributes
    ----------
    train_set : list of pixelmaps
        Training images.
    test_set : list of pixelmaps
        Testing images.
    simulator : `IONetwork`
        Network used.
    progress_results : dict, optional
        progress results if monitoring it.
    ws_name : str, optional
        Name on websocket server if activated.

    Parameters
    ----------
    OutputClass : class
        Class of the output NeuronGroup.
    SynapseClass : class
        Class of the Synapses linking in and out.
    train_set : list if pixelmaps
        List of training images.
    test_set : list of pixelmaps
        List of testing images.
    backup_mode : bool, optional
        Set to True if regenerated from backup.

    """

    train_set = []
    test_set = []

    _offline_mode = False

    def __init__(self, OutputClass, SynapseClass, train_set, test_set,
                 backup_mode=False):
        out_ng = OutputClass.customize().with_event(
            name='depress',
            cond='(timestep(t_rel, dt) == timestep({}*ms, dt)'.format(T01/ms)
            + ' or timestep(t_rel, dt) == timestep({}*ms, dt))'.format(T11/ms)
            + ' and depress == 1',
            code='v = v_trigger',
            when='start'
        ).with_event(
            name='potentiate',
            cond='(timestep(t_rel, dt) == timestep({}*ms, dt)'.format(T03/ms)
            + ' or timestep(t_rel, dt) == timestep({}*ms, dt))'.format(T13/ms)
            + ' and potentiate == 1',
            code='v = v_trigger',
            when='start'
        ).with_event(
            name='hold',
            cond='timestep(t_rel, dt) == timestep({}*ms, dt)'.format(T10/ms)
            + ' and hold == 1',
            code='v = v_trigger',
            when='start'
        ).with_variable('t_rel : second').with_variable(
            'depress : 1'
        ).with_variable('potentiate : 1').with_variable('hold : 1').create(
            N=class_amount * class_size, name='output')

        self.simulator = IONetwork(
            InputClass(test_set[FIRST]['size'], name='input'),
            out_ng, SynapseClass)

        self.train_set = train_set
        self.test_set = test_set
        if progress_monitoring['active']:
            self.progress_results = {'steps': [], 'values': []}

        if websocket_logging['active'] and not backup_mode:
            try:
                get_event_loop().run_until_complete(self._get_ws_name())
            except ConnectionRefusedError as e:
                self._offline_mode = True
                logging.warning("Could not connect to Websocket server!" +
                                " Entering offline mode...")

    async def _get_ws_name(self):
        """Get a name from the websocket server."""
        async with connect(
                websocket_logging['server']) as ws:
            await ws.send(dumps({
                'type': 'hello',
                'name': '',
                'payload': {
                    'tau_LTP': str(tau_LTP),
                    'tau_LTD': str(tau_LTD),
                    'ALTP': str(ALTP),
                    'ALTD': str(ALTD),
                    'aLTP': str(aLTP),
                    'aLTD': str(aLTD),
                    'w_max': str(w_max),
                    'train_data_size': str(train_data_size),
                    'test_data_size': str(test_data_size),
                    'v_rest': str(v_rest),
                    'v_threshold': str(v_threshold),
                    'v_trigger': str(v_trigger)
                }
            }))
        answer = loads(await ws.recv())
        self.ws_name = answer['payload']

    async def _send_training_results(self, id, value):
        """
        Sends training results to the websocket server.

        Parameters
        ----------
        id : int
            Step of the result.
        value : int
            Value of the result.

        Raises
        ------
        TrainerError
            If data is not accepted by the server.
        """

        async with connect(
                'ws://cuallado.fr:8087') as websocket:
            await websocket.send(dumps({
                'type': 'training',
                'name': self.ws_name,
                'payload': {
                    'id': id,
                    'value': value
                }
            }))
            answer = loads(await websocket.recv())
            if not answer['payload']:
                raise TrainerError('Could not send data to Websocket server!')

    def test_network(self, dry_run=False):
        """
        Tests network capacity.

        Parameters
        ----------
            dry_run : bool, optional
                Whether to restore network after test.

        Returns
        -------
        results : dict
            image (list): Class of image tested.

            success (list): Whether it was successful or not.

            rate (float): Success rate of testing.

            success_num (int): Number of successes.
        """

        if dry_run:
            self.simulator.store("dry_test")

        # TESTING PHASE
        results = {'image': [], 'success': [], 'rate': 0, 'success_num': 0}
        success = 0
        for image in tqdm(self.test_set, desc="Testing Network"):
            indices, times = image2spikes(image['pixelmap'])
            self.simulator['input'].set_spikes(
                indices, times + self.simulator.t)

            data = self.simulator.run(cycle_time, record_output_spikes=True)

            run_results = get_class_spike_number(data, class_size,
                                                 class_amount)
            logging.debug(run_results)
            best = {'class': 0, 'value': -1}
            canceled = False
            for i, v in enumerate(run_results):
                if v == best['value']:
                    canceled = True
                elif v > best['value']:
                    canceled = False
                    best = {'class': i, 'value': v}

            results['image'].append(image['class'])
            if best['class'] == image['class'] and not canceled:
                success += 1
                results['success'].append(True)
            else:
                results['success'].append(False)

        results['rate'] = success/len(self.test_set) * 100
        results['success_num'] = success
        if dry_run:
            self.simulator.restore("dry_test")

        return results

    def train(self):
        """
        Runs a full training step on the network.

        Raises
        ------
        TrainerError
            If there is an issue while reading the picture.
        """
        image = self.train_set.pop(0)
        indices, times = image2spikes(image['pixelmap'])
        if len(indices) == 0:
            raise TrainerError(
                {"message": "Working on empty picture!",
                 "picture": train_data_size - len(self.train_set)})

        self.simulator['input'].set_spikes(indices, times + self.simulator.t)
        data = self.simulator.run(cycle_time, record_output_spikes=True)
        spiking_classes, non_spiking_classes = get_class_spike_ids(
            data, class_size, class_amount)

        self._set_markers(image, spiking_classes, non_spiking_classes)

        self._apply_training(indices)

        if (progress_monitoring['active']
                and len(self.train_set) % progress_monitoring['step'] == 0):
            test_results = self.test_network(dry_run=True)
            self.progress_results['steps'].append(
                train_data_size - len(self.train_set))
            self.progress_results['values'].append(test_results['rate'])
            if websocket_logging['active'] and not self._offline_mode:
                try:
                    get_event_loop().run_until_complete(
                        self._send_training_results(
                            train_data_size - len(self.train_set),
                            test_results['rate']
                        ))
                except ConnectionRefusedError as e:
                    self._offline_mode = True
                    logging.warning("Could not connect to Websocket server!" +
                                    " Entering offline mode...")

    def _set_markers(self, image, spiking_classes, non_spiking_classes):
        """
        Uses image data to set stimulus markers on neurons.

        Parameters
        ----------
        image : dict
            MNIST image to be studied.
        spiking_classes : list of int
            Array of neurons spiking in each class.
        non_spiking_classes : list of in
            Array of neurons not spiking in each class.
        """
        hold_list = []
        for class_id in range(class_amount):
            # Counting spiking neurons
            spiking_neurons = spiking_classes[class_id]
            non_spiking_neurons = non_spiking_classes[class_id]
            number_spikes = len(spiking_neurons)

            # If neurons should spike
            if class_id == image['class']:
                a = [
                    class_id * class_size + n
                    for n in range(class_size)
                ]
                hold_list += a
                if number_spikes < active_threshold:
                    for _ in range(active_threshold - number_spikes):
                        neuron = rng.choice(non_spiking_neurons)
                        hold_list.remove(neuron)
                        non_spiking_neurons.remove(neuron)
                        self.simulator.output.potentiate[neuron] = 1

            # If neurons should not spike and too many did
            elif number_spikes > inactive_threshold:
                for _ in range(number_spikes - inactive_threshold):
                    neuron = rng.choice(spiking_neurons)
                    spiking_neurons.remove(neuron)
                    self.simulator.output.depress[neuron] = 1

        for neuron in hold_list:
            self.simulator.output.hold[neuron] = 1

    def _apply_training(self, indices):
        """
        Runs the training section on the network.

        Parameters
        ----------
        indices : list of int
            indices of spiking neurons for input.
        """
        training_times = ([T02 for _ in range(len(indices))]
                          + [T12 for _ in range(len(indices))])

        for _ in range(train_step):
            self.simulator.output.t_rel = -self.simulator.output.dt
            self.simulator['input'].set_spikes(
                indices * 2, training_times + self.simulator.t)
            self.simulator.run(train_time)

        self.simulator.output.potentiate = 0
        self.simulator.output.depress = 0
        self.simulator.output.hold = 0

    def store(self):
        """Save the current progress to `runtime/`."""
        # Reducing simulator to its values
        temp_simulator = self.simulator
        if not os.path.isdir('runtime'):
            os.mkdir('runtime')
        self.simulator.store(filename='runtime/network_backup.dat')
        self.simulator = None
        pickle_file = open('runtime/trainer_backup.dat', mode='wb')
        pickle.dump(self, pickle_file)
        pickle_file.close()

        self.simulator = temp_simulator

    @classmethod
    def restore(cls, OutputClass, SynapseClass):
        """Load the current progress from `runtime/`."""
        save_file = open('runtime/trainer_backup.dat', mode='rb')
        old_trainer = pickle.load(save_file)
        save_file.close()

        res = ZengTrainer(OutputClass, SynapseClass, old_trainer.train_set,
                          old_trainer.test_set, backup_mode=True)

        temp_sim = res.simulator
        res.__dict__.clear()
        res.__dict__.update(old_trainer.__dict__)
        res.simulator = temp_sim
        res.simulator.restore(filename='runtime/network_backup.dat')

        return res

    def clean(self):
        """Remove progress files."""
        os.remove('runtime/trainer_backup.dat')
        os.remove('runtime/network_backup.dat')


class TrainerError(Exception):
    pass
