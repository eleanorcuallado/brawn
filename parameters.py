"""
File regrouping all tweakable parameters of the simulation.
"""

from brian2 import ms, mV
import logging
# ---- Simulation Parameters ---- #

# Classification parameters
class_size = 5
class_amount = 10

# Simulation parameters
cycle_time = 30 * ms
train_time = 2 * cycle_time
dt = 0.1*ms

# Data size
train_data_size = 150
test_data_size = 15

# Training phase
train_step = 2
active_threshold = 2
inactive_threshold = 0

# Training timing parameters
T00 = 5 * ms
T01 = 10 * ms
T02 = 15 * ms
T03 = 20 * ms
T10 = cycle_time + T00
T11 = cycle_time + T01
T12 = cycle_time + T02
T13 = cycle_time + T03

# Synapses parameters
tau_LTP = 20*ms        # Amplitude of decay of Potentiation learning
tau_LTD = 20*ms        # Amplitude of decay of Depression learning
ALTP = 1               # Amplitude of trace upating for potentiation
ALTD = -1              # Amplitude of trace updating for depression
aLTP = 2 * 10**(-2)    # Potentiation learning rate
aLTD = 2.4 * 10**(-2)  # Depression learning rate
w_max = 0.4           # Max weight

# Neurons parameters
v_rest = 0*mV        # Resting membrane voltage
v_threshold = 200*mV   # Voltage required to trigger spike
v_trigger = 200*mV  # Voltage triggering spikes

# Monitoring
progress_monitoring = {'active': True, 'step': 260}
weight_monitoring = {'active': False, 'record': True}
voltage_monitoring = {'active': False, 'record': True}

# Program parameters
backup_threshold = int(train_data_size / 100)
verbose = logging.INFO
plot_per_class_success = True
use_backup = True
clean_backup = False
websocket_logging = {'active': False, 'server': 'ws://'}

if __name__ == '__main__':
        print("Do not run parameters directly!")
