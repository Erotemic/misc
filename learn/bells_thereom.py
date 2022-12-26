"""
https://en.wikipedia.org/wiki/Bell%27s_theorem
https://www.youtube.com/watch?v=ZuvK-od647c&t=58s at 4:20
https://gist.github.com/linuxelf001/488559

https://nbviewer.ipython.org/github/qutip/qutip-notebooks/blob/master/examples/quantum-gates.ipynb
https://nbviewer.ipython.org/github/jrjohansson/qutip-lectures/blob/master/Lecture-0-Introduction-to-QuTiP.ipynb

https://en.wikipedia.org/wiki/Bell_state

Requirements:

    QuTiP

    # For viz
    sudo apt-get install texlive-extra-utils

    # fix for permission issue
    # https://stackoverflow.com/questions/52861946/imagemagick-not-authorized-to-convert-pdf-to-an-image
    sed -i 's/^.*policy.*coder.*none.*PDF.*//' /etc/ImageMagick-6/policy.xml


    Might also want to try QiSkit
    https://qiskit.org/documentation/tutorials/circuits/01_circuit_basics.html
"""

import qutip
import kwplot
kwplot.autompl()


def draw_circuit(circuit):
    import io
    import numpy as np
    from PIL import Image
    file = io.BytesIO()
    raw = circuit._raw_png()
    file.write(raw)
    file.seek(0)
    pil_img = Image.open(file).convert('L')
    imdata = np.asarray(pil_img)
    return imdata

from qutip.qip.operations import cnot
from qutip.qip.circuit import QubitCircuit


# This circuit creates the "Bell State"
# which maximally entangles two input qubits.
num_qubits = 2
bell_circuit = QubitCircuit(num_qubits, input_states=["e1", "e2", "c1", "c2"], num_cbits=2)
bell_circuit.add_gate("SNOT", targets=0)  # snot is Hadamard
bell_circuit.add_gate("CNOT", controls=[0], targets=[1])
bell_circuit.add_measurement("M0", targets=[0], classical_store=0)
bell_circuit.add_measurement("M1", targets=[1], classical_store=1)


circuit = bell_circuit
kwplot.imshow(draw_circuit(bell_circuit))


# qutip.qubit_states()

# Create a system of two electrons
e1 = qutip.basis(dimensions=2, n=0)
e2 = qutip.basis(dimensions=2, n=1)
# This state represents two electrons
input_state = qutip.tensor(e1, e2)


# We can measure, these. It wont matter because we are going to make the
# bell State
initial_measurement = qutip.Measurement("start", targets=[0])
collapsed1, probs1 = initial_measurement.measurement_comp_basis(e1)
collapsed2, probs2 = initial_measurement.measurement_comp_basis(e2)
collapsed3, probs3 = initial_measurement.measurement_comp_basis(input_state)
print('probs1 = {!r}'.format(probs1))
print('probs2 = {!r}'.format(probs2))
print('probs3 = {!r}'.format(probs3))
print('collapsed1 = {!r}'.format(collapsed1))
print('collapsed2 = {!r}'.format(collapsed2))
print('collapsed3 = {!r}'.format(collapsed3))

# This is an entangled state
output_state = bell_circuit.run(input_state)
print('output_state = {!r}'.format(output_state))

output_stats = bell_circuit.run_statistics(input_state)
print('output_stats.final_states = {!r}'.format(output_stats.final_states))
print('output_stats.cbits = {!r}'.format(output_stats.cbits))
print('output_stats.probabilities = {!r}'.format(output_stats.probabilities))

final_measurment1 = qutip.Measurement("final1", targets=[0])
collapsed4, probs4 = final_measurment1.measurement_comp_basis(output_state)
final_measurment2 = qutip.Measurement("final2", targets=[1])
collapsed5, probs5 = final_measurment2.measurement_comp_basis(output_state)


# Do a rotation of each qbit independently


num_qubits = 2

import numpy as np
oort = 1 / np.sqrt(2)

qutip.basis(dimensions=2, n=0)


rando_circuit = .QubitCircuit(num_qubits, num_cbits=2, input_states=["a", "b", "c1", "c2"])
rando_circuit.add_gate("RX", arg_value=0.5, targets=[0])
rando_circuit.add_gate("RY", arg_value=0.5, targets=[1])
# rando_circuit.add_gate("SNOT", targets=0)  # SNOT is Hadamard
# rando_circuit.add_gate("CNOT", controls=[0], targets=[1])
rando_circuit.add_measurement("M0", targets=[0], classical_store=0)
rando_circuit.add_measurement("M1", targets=[1], classical_store=1)
kwplot.imshow(draw_circuit(rando_circuit))

a = qutip.basis(dimensions=2, n=0)
b = qutip.basis(dimensions=2, n=1)
# a = oort * qutip.basis(2, 0) + oort * qutip.basis(2, 1)
# b = oort * qutip.basis(2, 0) + oort * qutip.basis(2, 1)
input_state = qutip.tensor(a, b)

output_state = rando_circuit.run(input_state)
print('output_state = {!r}'.format(output_state))

output_stats = rando_circuit.run_statistics(input_state)
print('output_stats.final_states = {!r}'.format(output_stats.final_states))
print('output_stats.cbits = {!r}'.format(output_stats.cbits))
print('output_stats.probabilities = {!r}'.format(output_stats.probabilities))

final_measurment1 = qutip.Measurement("final1", targets=[0])
collapsed1, probs1 = final_measurment1.measurement_comp_basis(a)
print('probs1 = {!r}'.format(probs1))
print('collapsed1 = {!r}'.format(collapsed1))


final_measurment2 = qutip.Measurement("final2", targets=[1])
collapsed2, probs2 = final_measurment2.measurement_comp_basis(output_state)
print('probs2 = {!r}'.format(probs2))
print('collapsed2 = {!r}'.format(collapsed2))

op0 = qutip.basis(2, 0) * qutip.basis(2, 0).dag()
qutip.measurement.measure_observable(a, op0)
