def orig():
    import ubelt as ub
    # 7 words from a 7776 dictionary should beat the Type0-Adversary
    # Word security level
    import math
    vocab_size = 25487
    vocab_size = 7776
    security_levels = {}
    security_levels['words-4'] = vocab_size ** 4
    security_levels['words-5'] = vocab_size ** 5
    security_levels['words-6'] = vocab_size ** 6
    security_levels['words-7'] = vocab_size ** 7
    security_levels['words-8'] = vocab_size ** 8
    security_levels['words-12'] = vocab_size ** 12
    security_levels['words-35'] = vocab_size ** 35
    security_levels['sha1']   = 16 ** 40
    security_levels['sha256'] = 16 ** 64
    security_levels['sha512'] = 16 ** 128
    security_levels['abc-20'] = 26 ** 20
    security_levels['hex-12'] = 16 ** 12
    security_levels['hex-20'] = 16 ** 20
    security_levels['hex-32'] = 16 ** 32
    security_levels['hex-16'] = 16 ** 16


    # Type 1 Civ Adversarial Actor
    # population = 7.674e9
    # num_devices = population * 10

    # Type 0 Civ Adversarial Actor
    population = 3e8
    num_devices = population * 1

    # Large Adversarial Actor
    #num_devices = 1e6

    # https://gist.github.com/Chick3nman/e4fcee00cb6d82874dace72106d73fef
    # Based on rtx3090 attacking eth wallet
    device_attempts_per_second = 3934 * 1000  # Based on rtx3090 attacking eth wallet

    attempts_per_second = device_attempts_per_second * num_devices
    def years_to_crack(x):
        return (x / attempts_per_second) / 60 / 60 / 24 / 365
    security_bits = ub.map_vals(lambda x: math.log(x) / math.log(2), security_levels)
    security_years = ub.map_vals(years_to_crack, security_levels)

    print(ub.repr2(ub.sorted_vals(security_bits), align=':', precision=2))
    print(ub.repr2(ub.sorted_vals(security_years), align=':', precision=2))

    bits_to_years = {
        b: years_to_crack((2 ** b)) for b in range(40, 160, 5)
    }
    print(ub.repr2(ub.sorted_vals(bits_to_years), align=':', precision=6))
    # number of words to hit 80 bits of entropy with diceware
    vocab_size = 7776
    vocab_size ** X == 2 ** 80
    math.log(vocab_size ** 8) / math.log(2)
    math.log(2 ** 80) / math.log(vocab_size)

    import english_words
    import random
    pool = list(english_words.english_words_set)
    rng = random.SystemRandom()
    chosen = rng.choices(pool, k=8)
    print('_'.join(chosen))


def main():
    import ubelt as ub
    import math

    # Enumerate password schemes to test the robustness of
    phrase_scheme_basis = {
        'vocab_size': [
            7776,
            # 25487
        ],
        'num_words': [4, 6, 7, 8],
    }

    password_schemes = []
    for vocab_size in phrase_scheme_basis['vocab_size']:
        for num_words in phrase_scheme_basis['num_words']:
            password_schemes.append(
                {
                    'name': 'words-{}-{}'.format(num_words, vocab_size),
                    'base': vocab_size,
                    'num': num_words,
                }
            )

    # Add in extra information
    for scheme in password_schemes:
        scheme['states'] = scheme['base'] ** scheme['num']
        scheme['entropy'] = math.log(scheme['states']) / math.log(2)
        scheme['security_against'] = {}

    # Enumerate state of the art devices that can crack passwords
    devices = {
        'rtx3090': {
            # https://gist.github.com/Chick3nman/e4fcee00cb6d82874dace72106d73fef#file-rtx_3090_v6-1-1-benchmark-L1006
            # Based on rtx3090 attacking eth wallet
            'name': 'RTX 3090',
            'attempts_per_second': 3934 * 1000,
        }
    }

    # Enumerate theoretical scales to bound how many devices a threat actor
    # might have
    scales = {
        'world_population_2019': 7.674e9,  # 7 billion
        'us_population_2019': 328.2e6,     # 300 million
        'china_population_2021': 1_397_897_720,  # 1 billion
        'nyc_population_2019': 8.419e6,  # 8 million
        '2020_gpu_shipments': 41e6,  # 46 million
        'austin_2020': 1e6  # about 1 million.
    }

    device = devices['rtx3090']

    thread_models = [
        {
            'name': 'Type0-Earth',
            'comment': ub.paragraph(
                '''
                Ridiculous case where every person on the planet in 2019 has a
                RTX 3090 attacking your password
                '''),
            'attempts_per_second': scales['world_population_2019'] * device['attempts_per_second']
        },
        {
            'name': 'Type0-China',
            'attempts_per_second': scales['china_population_2021'] * device['attempts_per_second']
        },
        {
            'name': 'Type0-US',
            'attempts_per_second': scales['us_population_2019'] * device['attempts_per_second']
        },
        {
            'name': 'City-Austin',
            'attempts_per_second': scales['austin_2020'] * device['attempts_per_second']
        }
    ]

    def time_to_crack(states, attempts_per_second):
        seconds = states / attempts_per_second
        minutes = seconds / 60.
        hours = minutes / 60.
        days = hours / 24.
        years = days / 365.
        if minutes < 1:
            return (seconds, 'seconds')
        if hours < 1:
            return (minutes, 'minutes')
        if days < 1:
            return (hours, 'hours')
        elif years < 1:
            return (days, 'days')
        else:
            return (years, 'years')

    for scheme in password_schemes:
        for threat_model in thread_models:
            states = scheme['states']
            attempts_per_second = threat_model['attempts_per_second']
            scheme['security_against'][threat_model['name']] = {
                'time': time_to_crack(states, attempts_per_second),
            }

    for scheme in password_schemes:
        print('scheme = {}'.format(ub.repr2(scheme, nl=2, precision=4)))
