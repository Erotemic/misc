

probs = {
    '0.0m': 0.65,
    '0.5m': 0.51,
    '1.0m': 0.06,
}


for key, transmit_prob in probs.items():
    print('===================')
    print('@ Distance = {!r}'.format(key))
    print('transmit_prob = {!r}'.format(transmit_prob))
    dan_probability  = transmit_prob
    us_probability   = dan_probability * transmit_prob
    jess_probability = us_probability * transmit_prob
