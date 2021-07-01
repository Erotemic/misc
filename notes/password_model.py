"""
Recently, I was put into a circumstance where I needed to come up with and
remember a password I would be required to manually type in. Awful, I know.


My first thought was a classic "correct horse battery staple" style password
introduced by Randall Monroe in 2011 [1]_. My second thought was: is that good
enough anymore? (spoiler: no) And my third thought was: how many words do I
need to make a password I that was utterly unguessable? (spoiler: 9 words, but
7 is probaly ok).

At its core the problem is relatively simple. I imagine a game where I get to
choose any password, and then my adversary/opponent has to guess the password.
If they guess it within my lifetime I lose, otherwise I win.

When I choose a password, I really am choosing some pattern, and a length.
The total number of possible passwords I could have chosen represents the
"strength" of the password (i.e. its entropy).

Next, we have to make some assumptions about the adversary. This is known as
choosing a threat model. We assume that the adversary knows what pattern I
chose, so they can theoretically enumerate all possibilities. The main question
is: how fast can they do it? Or more precisely, how fast can they make attempts
against my password?

This is a tricky question to answer because it depends a lot on what service
the password is being used for, and how secure their password validation scheme
is.

To help me estimate how fast an adversary may be able to attack me I looked up
these reference benchmarks that detail how fast an RTX 3090 GPU can make
attempts at various password schemes:

https://gist.github.com/Chick3nman/e4fcee00cb6d82874dace72106d73fef#file-rtx_3090_v6-1-1-benchmark-L1006


For instance, in VeraCrypt, against the ultra secure Streebog-512 + XTS 1536
bit, a 3090 can make 46 attempts per second.

Whereas for a normal case, like an, Ethereum Wallet a 3090 can make 3,934,000
attempts per second.

And for the ultra-insecure case, a service that stores passwords in plaintext,
a 3090 can make 121,000,000,000 attempts per second.

Now, any threat-actor worth their salt isn't going to be running on a single
GPU. So the question is, how many GPUs could a threat actor have?

This is an incredibly hard question to answer percicely, but we can answer it
"good-enough" by overestimating the compute power the adversary might have.
This puts an upper bound on the threat actors we may encounter and allows us to
be confident that our password won't be cracked.

So I imagine a few different scales of actors, each of which is simply used to
define a number N, which is the number of RTX 3090 GPUs that our hypothetical
adversary will have access to.

    * A random lone hacker, N=1
    * A small-city scale actor, N=100,000
    * A large-city scale actor, N=1,000,000
    * A small-nation-state scale actor, N=100,000,000
    * A large-nation-state scale actor, N=1,000,000,000
    * A world-scale actor, N=10,000,000,000

At the largest and most ridiculous scale we imagine the world as a Type-0.73
civilization [7] where each of the 10 billion people on the planet have an
RTX-3090 GPU and one goal: crack your password.

Can we beat them? Yes.

If we use a 9-word password, a World-Scale actor has no chance of even breaking
a plaintext password. Even an 8-word password would take 350 years to crack,
although they could enumerate each word on STDOUT in only 1.7 years.

Moving to a 7 word password, we start loosing some security against the
world-scale actor. They can break our plaintext service in 16 days, and a weak
hashing scheme like plain md5 will be cracked in 30 days. However, for modern
security-minded services like an ETH wallet, the world scale actor will still
take 1385 years.

Furthermore, the world scale actor is an absurd upper bound. The number of GPUs
shipped in 2020 was only around 46 million, and only a fraction of those were
anywhere near as powerful as an RTX 3090. A small nation will take about 8
years to crack a weak scheme like md5, but a metropolis (10 million) would take
about 80 years.

Moving down to 6 words, you are only safe against small-city scale actors
(100,000 GPUs) on weak password schemes, although even a world scale actor
still wont be able to crack your VeraCrypt container.

What does 4 words get you these days? Not much. Even VeraCrypt would go down to
a small-city sized attack, and a random lone hacker could crack a weak password
storage scheme in 15 minutes.

I think the next aspect to explore is cost based on AWS compute.

In reality Nation State actors probably have somwehere between a small city and
a large city worth of compute based on my educated guess, and that's only if
they throw everything they've got at you.


AWS has roughly 1.4 million servers [9]_.

Rough cost per gpu per hour $1.045 [10]_.

RTX 3090 runs at 370W

1 kWh cost $0.12


References:
    [1] https://xkcd.com/936/
    [2] https://twitter.com/erotemic/status/1408852635093016582
    [3] https://en.wikipedia.org/wiki/Diceware
    [4] https://en.wikipedia.org/wiki/PBKDF2
    [5] https://theconversation.com/a-computer-can-guess-more-than-100-000-000-000-passwords-per-second-still-think-yours-is-secure-144418
    [6] https://stackoverflow.com/questions/54733868/how-many-attempts-per-second-can-a-password-cracker-actually-make
    [7] https://en.wikipedia.org/wiki/Kardashev_scale
    [8] https://www.reddit.com/r/aws/comments/6qkhfb/how_many_gpus_does_aws_have_in_total/

    [9] https://www.quora.com/How-many-servers-does-AWS-have#:~:text=Cloud%20hardware%20is%20very%20interesting,more%20than%201%2C000%2C000%20physical%20servers.
    [10] https://aws.amazon.com/ec2/instance-types/p3/

Requirements:
    ubelt

"""
import ubelt as ub
import math
import string


def build_password_strategy():
    """
    Returns information - specifically the entropy - about possible schemes,
    patterns, or strategry we might use to construct a password. We will
    analyize the security of each against.
    """
    # List different candidate patterns for remembering passwords
    password_schemes = []

    # Enumerate character-based password schemes
    alphabets = {
        'lower': len(string.ascii_lowercase),
        'upper': len(string.ascii_uppercase),
        'digits': len(string.digits),
        'special': len(string.punctuation),
    }
    # Google raondom passwords are 15 chars long
    for num in [8, 15, 20]:
        base = sum(alphabets.values())
        password_schemes.append(
            {
                'name': 'chars-{}-{}'.format(num, base),
                'num': num,
                'base': base,
            }
        )

    # Enumerate word-based password schemes
    phrase_scheme_basis = {
        'vocab_size': [
            7776,
            # 25487
        ],
        'num_words': [4, 5, 6, 7, 8, 9, 10],
    }

    for vocab_size in phrase_scheme_basis['vocab_size']:
        for num_words in phrase_scheme_basis['num_words']:
            password_schemes.append(
                {
                    'name': 'words-{}-{}'.format(num_words, vocab_size),
                    'base': vocab_size,
                    'num': num_words,
                }
            )

    password_schemes.append(
        {
            'name': 'chbs-{}-{}'.format(4, 2048),
            'base': 2048,
            'num': 4,
        }
    )

    # Postprocess password schemes
    for scheme in password_schemes:
        scheme['states'] = scheme['base'] ** scheme['num']
        scheme['entropy'] = math.log(scheme['states']) / math.log(2)
        scheme['security_against'] = {}

    return password_schemes


def build_threat_models():
    """
    Returns the devices our adversaries might have, and the scales they might
    operate at.
    """
    # Enumerate how fast certain devices can make attempts on particular
    # password schemes
    # https://gist.github.com/Chick3nman/e4fcee00cb6d82874dace72106d73fef#file-rtx_3090_v6-1-1-benchmark-L1006
    devices = [
        {
            'name': 'RTX_3090',
            'watts': 370.0,
            'benchmarks': [

                # {
                #     # Based on rtx3090 attacking eth wallet
                #     # This is a standin for a reasonably secure password hashmode
                #     'hashmode': 'ETH-PBKDF2-HMAC-SHA256',
                #     'attempts_per_second': 3934 * 1e3,
                # },

                # {
                #     # This is actually the worst case (how fast to print to stdout)
                #     'hashmode': 'STDOUT',
                #     'attempts_per_second': 24549.4 * 1e9,
                # },

                {
                     # A "Strong" modern (2021) scheme
                    'hashmode': 'VeraCrypt SHA512 + XTS 512 bit',
                    'attempts_per_second': 2837,
                },
                # {
                #      A "Stronger" modern (2021) scheme
                #     'hashmode': 'VeraCrypt Streebog-512',
                #     'attempts_per_second': 46,
                # },

                {
                    # This is a reasonable worst-case password hashmode
                    'hashmode': 'Plaintext',
                    'attempts_per_second': 121 * 1e9,
                },


                {
                    # A "Good" modern (2021) scheme
                    'hashmode': 'bcrypt $2*$, Blowfish',
                    'attempts_per_second': 96662,
                },

                {
                    # A "Weak" but still used scheme
                    'hashmode': 'md5',
                    'attempts_per_second': 65079.1 * 1e6,
                }
            ]
        }
    ]

    type_1_watts = 1.74e17
    type_1_watts / 350

    # Enumerate theoretical scales to bound how many devices a threat actor
    # might have
    scales = [
        {'name': 'Randos',         'num_devices': 1e0},    # exactly 1.

        {'name': 'Randos100',      'num_devices': 100e0},  # 100.
        {'name': 'Randos1000',     'num_devices': 1e3},    # 1,000.
        {'name': 'SmallCity',      'num_devices': 100e3},  # 100,000
        # {'name': 'LargeCity',      'num_devices': 1e6},    # 1 million
        # {'name': 'Metropolis',     'num_devices': 10e6},   # 10 million
        {'name': 'SmallNation',    'num_devices': 100e6},  # 100 million
        # {'name': 'LargeNation',    'num_devices': 1e9},    # 1 billion
        {'name': 'Type0.73-World', 'num_devices': 10e9},   # 10 billion
        {'name': 'Type1-World',    'num_devices': 10e14},  # Distant Future (maybe, it's up to us)

        # 'Austin_2020': 1e6,  # about 1 million.
        # 'NYC_2019': 8.419e6,  # 8 million
        # 'GPU_Shipments_2020': 41e6,  # 46 million
        # 'USA_2019': 328.2e6,     # 300 million
        # 'China_2021': 1_397_897_720,  # 1 billion
        # 'Earth_2019': 7.674e9,  # 7 billion
    ]

    # For our idealized purpose we will ignore the "zipties and baseball bat"
    # hacker device... because somebody is going to bring it up otherwise
    return devices, scales



def main():
    """
    Run password security analysis

    Example:
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc/notes'))
        >>> from password_model import *  # NOQA
        >>> main()
    """

    # Build our adversary and our strategies
    devices, scales = build_threat_models()

    password_schemes = build_password_strategy()

    # Other estimates or assumptions
    estimates = {
        # estimated cost of using a kilowatt for an hour
        # http://www.wrecc.com/what-uses-watts-in-your-home/
        # https://www.coinwarz.com/mining/ethereum/calculator?h=100.00&p=1.00&pc=0.10&pf=0.00&d=6504945223037478.00000000&r=2.00000000&er=0.06440741&btcer=34726.37000000&ha=MH&hc=19999.00&hs=-1&hq=1
        'dollars_per_kwh': 0.10,
    }

    # import itertools as it
    # for device, scheme, (scale_name, num_devices), benchmark = it.product(
    #     devices, password_schemes.items(), device['benchmarks'])

    rows = []
    for device in devices:
        for scheme in password_schemes:
            for scale in scales:
                for benchmark in device['benchmarks']:

                    attempts_per_second = scale['num_devices'] * benchmark['attempts_per_second']

                    states = scheme['states']
                    seconds = states / attempts_per_second

                    hours = seconds / 3600.
                    device_kilowatts = device['watts'] / 1000.
                    device_dollars_per_hour = device_kilowatts * estimates['dollars_per_kwh']
                    cost_per_device = device_dollars_per_hour * hours
                    cost = cost_per_device * scale['num_devices']

                    total_kilowatts = device_kilowatts * scale['num_devices'] * hours

                    row = {
                        'scheme': scheme['name'],
                        'entropy': scheme['entropy'],

                        'hashmode': benchmark['hashmode'],

                        'device': device['name'],
                        'scale': scale['name'],
                        'num_devices': scale['num_devices'],

                        'seconds': seconds,
                        'cost': cost,

                        'kilowatts': total_kilowatts,
                        'hours': hours,
                        'dollars_per_kwh': estimates['dollars_per_kwh'],
                    }
                    rows.append(row)

    import pandas as pd
    df = pd.DataFrame(rows)
    df = df.sort_values('entropy')

    def humanize_dollars(d):
        return '${:4.02g}'.format(d)


    df = df[df['device'] == 'RTX_3090']
    df['htime'] = df['seconds'].apply(humanize_seconds)
    df['hcost'] = df['cost'].apply(humanize_dollars)
    df['num_devices'] = df['num_devices'].apply(int)


    hashmodes = sorted([d['hashmode'] for d in device['benchmarks']])

    # https://github.com/pandas-dev/pandas/issues/18066
    for hashmode in hashmodes:
        print('\n---')
        print('hashmode = {!r}'.format(hashmode))
        subdf = df
        subdf = subdf[subdf['hashmode'] == hashmode]
        subdf = subdf.sort_values(['entropy', 'num_devices'])
        p = subdf.pivot(['entropy', 'hcost', 'scheme'], ['num_devices', 'scale'], 'htime')
        # p.style.applymap(color_cases)
        print(p)


def humanize_seconds(seconds):
    minutes = seconds / 60.
    hours = minutes / 60.
    days = hours / 24.
    years = days / 365.
    if minutes < 1:
        raw = (seconds, 'seconds')
    elif hours < 1:
        raw = (minutes, 'minutes')
    elif days < 1:
        raw = (hours, 'hours')
    elif years < 1:
        raw = (days, 'days')
    else:
        raw = (years, 'years')

    count, unit = raw
    count_ = round(count, 4)
    ret = '{:.4g} {}'.format(count_, unit)

    if 1:
        if years > 1e5:
            # Blue is VERY safe
            ret = ub.color_text(ret, 'blue')
        elif years > 80:
            # Green is VERY safe
            ret = ub.color_text(ret, 'green')
        elif years > 10:
            ret = ub.color_text(ret, 'yellow')
        else:
            ret = ub.color_text(ret, 'red')

    return ret


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/notes/password_model.py
    """
    main()
