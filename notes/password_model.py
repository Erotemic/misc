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

Rough dollars per gpu per hour $1.045 [10]_.

RTX 3090 runs at 370W

1 kWh cost $0.12


TODO:
    Discuss side channel and social engineering
    Discuss two-factor authentication
    Discuss password protection [12]_.


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
    [11] https://xkcd.com/538/

    [12] https://monzo.com/blog/2021/11/18/protecting-our-most-sensitive-secrets

Requirements:
    pip install ubelt
    sudo apt install texlive texlive-latex-extra texlive-fonts-recommended dvipng
    sudo apt install texlive-latex-recommended texlive-latex-extra texlive-luatex latexmk -y
    sudo apt install texlive-latex-extra texlive-fonts-recommended dvipng cm-super

    luaotfload-tool --update
    pip install latex


"""
import ubelt as ub
import math
import string
from functools import partial


MODE = ub.argval('--MODE', default='full')
assert MODE in {'full', 'big', 'small'}


def build_password_strategy():
    """
    Returns information - specifically the entropy - about possible schemes,
    patterns, or strategry we might use to construct a password. We will
    analyize the security of each against.

    Example:
        password_schemes = build_password_strategy()
        print('password_schemes = {}'.format(ub.repr2(password_schemes, nl=1)))
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

    if MODE == 'full':
        # Google random passwords are 15 chars long
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
        # 'num_words': [6, 7, 8, 9],
    }

    if MODE == 'small':
        phrase_scheme_basis['num_words'] = [6, 7, 8]
    elif MODE == 'big':
        phrase_scheme_basis['num_words'] = [6, 7, 8, 9]

    for vocab_size in phrase_scheme_basis['vocab_size']:
        for num_words in phrase_scheme_basis['num_words']:
            password_schemes.append(
                {
                    'name': 'Diceware-words-{}-{}'.format(num_words, vocab_size),
                    'base': vocab_size,
                    'num': num_words,
                }
            )

    naive_schemes = True
    if naive_schemes:
        password_schemes.append(naive_password_strategy())
        password_schemes.append(naive_password_strategy(
            required_caps=0, required_special=1, required_digits=0
        ))

    password_schemes.append(
        {
            'name': 'XKCD-CHBS-{}-{}'.format(4, 2048),
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


def naive_password_strategy(required_len=14, required_caps=1,
                            required_special=1, required_digits=1):
    """
    Simulate a "bad" password that meets typical password requirements

    Get a naive version of the N char min special char password One
    common strategy for getting a 14 char pass is using 2 words or a word
    and a date with misspellings, shuffled case, and a special char,
    which is probably _, -, ., !, or @

    Example:
        scheme = naive_password_strategy()
        print(f'scheme={scheme}')
    """
    # When people are forced to include a special character, this is the
    # liklihood they choose one of the following:
    # https://www.reddit.com/r/dataisbeautiful/comments/2vfgvh/most_frequentlyused_special_characters_in_10/
    special_char_freq = {
        '_': 0.332,
        '.': 0.304,
        '-': 0.086,
        '!': 0.065,
        '@': 0.052,
        '*': 0.032,
        '$': 0.019,
        '&': 0.009,
        '%': 0.007,
    }
    _total = sum(special_char_freq.values())
    special_char_prob = ub.map_vals(lambda x: x / _total, special_char_freq)

    # Only seach the most likely special chars
    naive_special_chars = {
        k: v for k, v in special_char_prob.items()
        if v > 0.05
    }

    if 0:
        import diceware
        wlpath = diceware.wordlist.get_wordlist_path('en')
        wlpath = diceware.wordlist.get_wordlist_path('en_securedrop')
        wordlist = list(diceware.wordlist.WordList(wlpath))
        word_lengths = sorted(map(len, wordlist))
        word_length_hist = ub.dict_hist(word_lengths)
    else:
        # Number of common password words with a specific length
        word_length_hist = {
            1: 10,
            2: 90,
            3: 582,
            4: 2279,
            5: 3350,
            6: 1313,
            7: 539,
            8: 22,
            9: 5,
            10: 2
        }

    # Also needs a number and special char
    required_word_len = required_len - 2

    # How many permutations of N words are there that get over the char limit?
    total_passwords = 0
    import itertools as it
    import functools
    import operator as op
    possible_num_word = [1, 2, 3]
    for num_words in possible_num_word:
        for ts in it.product(*[word_length_hist.items()] * num_words):
            ks = [k for k, v in ts]
            vs = [v for k, v in ts]
            # If the lengths are above, we can take any of these permutations
            # (with replacement)
            if sum(ks) > required_word_len:
                # Compute the number of phrases, then augment this with the
                # special properties.
                num_phrases = functools.reduce(op.mul, vs)

                # People might insert a special character at the start, middle,
                # or end, or predictably replace a letter.
                predictability_factor = 2
                num_special_locs = (num_words + 1) * predictability_factor
                special_factor = required_special * len(naive_special_chars) * num_special_locs

                # People might insert a digit at start, middle, or end, or maybe
                # inside of a word replacing a common letter.
                num_digit_locs = num_words + 1
                num_digits = 10 + 100  # usually a 1 or 2 digit number
                digit_factor = required_digits * num_digits * num_digit_locs

                # People might only shuffle the case of 1 or 2 letters.
                # usually at the beginning of words
                caps_factor = required_caps * num_words

                total = (
                    num_phrases *
                    (1 + special_factor) *
                    (1 + caps_factor) *
                    (1 + digit_factor)
                )
                total_passwords += total

    name_parts = ['naive', str(required_len)]
    if required_caps:
        name_parts.append('caps')

    if required_digits:
        name_parts.append('digit')

    if required_special:
        name_parts.append('special')

    name = '-'.join(name_parts)

    scheme = {
        'name': name,
        'num': 1,
        'base': total_passwords,
    }
    return scheme


def build_threat_models():
    """
    Returns the devices our adversaries might have, and the scales they might
    operate at.
    """
    # Enumerate how fast certain devices can make attempts on particular
    # password schemes
    # https://gist.github.com/Chick3nman/e4fcee00cb6d82874dace72106d73fef#file-rtx_3090_v6-1-1-benchmark-L1006
    # https://gist.github.com/Chick3nman/32e662a5bb63bc4f51b847bb422222fd#file-RTX_4090_v6.2.6.Benchmark

    if 0:
        # For developer hard codeing
        raw_hashcat_benchmarks = {
            'RTX_3090': 'https://gist.githubusercontent.com/Chick3nman/e4fcee00cb6d82874dace72106d73fef/raw/11ec7cf3c8c2627bf8b6a20673f2d571caa0bef9/RTX_3090_v6.1.1.Benchmark',
            'RTX_4090': 'https://gist.githubusercontent.com/Chick3nman/32e662a5bb63bc4f51b847bb422222fd/raw/265c25315440e0219e9c0406a56369ccaf640ac6/RTX_4090_v6.2.6.Benchmark',
        }
        parsed = {}
        for k, url in raw_hashcat_benchmarks.items():

            import parse
            header_parser1 = parse.Parser('Hashmode: {index} - {name}')
            header_parser2 = parse.Parser('* Hash-Mode {index} {name}')
            speed_parser = parse.Parser('Speed.#{test_num:d}{dots}: {rate} ({total}) @ {context}')
            fpath = ub.grabdata(url)

            entries = []
            lines = ub.Path(fpath).read_text().split('\n')
            part = None
            for line in lines:
                if line.startswith('Hashmode:') or line.startswith('* Hash-Mode'):
                    if part:
                        entries.append(part)
                    if line.startswith('Hashmode:'):
                        info = header_parser1.parse(line).named
                    if line.startswith('* Hash-Mode'):
                        info = header_parser2.parse(line).named
                    info['name'] = info['name'].strip()
                    info['name'] = info['name'].replace(']', ')')
                    info['name'] = info['name'].replace('[', '(')
                    iter_part = ''
                    if 'Iterations' in info['name']:
                        name, iter_part = info['name'].split('(Iterations')
                    else:
                        name = info['name']
                    name = name.strip()
                    if not name.startswith('('):
                        name = '(' + name + ')'
                    if iter_part:
                        name = name + ' (Iterations' + iter_part
                    info['name'] = name
                    part = {'header': info}
                if part is not None:
                    if line.startswith('Speed.'):
                        info = speed_parser.parse(line).named
                        info = ub.udict(info) - {'dots'}
                        num, unit = info['rate'].strip().split(' ')

                        if unit == 'GH/s':
                            mag = 1e9
                        elif unit == 'MH/s':
                            mag = 1e6
                        elif unit == 'kH/s':
                            mag = 1e3
                        elif unit == 'H/s':
                            mag = 1
                        else:
                            raise Exception
                        info['rate'] = float(num) * mag
                        part.setdefault('tests', []).append(info)
            if part:
                entries.append(part)

            hashmodes_of_interest = [
                'VeraCrypt Streebog-512',
                'HMAC-SHA256',
                'sha256($pass.$salt)',
                'MD5',
                'bcrypt $2*$, Blowfish',
                'AES Crypt (SHA256), k=8191',
                'Ethereum Wallet, PBKDF2-HMAC-SHA256',
                'VeraCrypt SHA512 + XTS 512 bit',
                'Plaintext',
            ]
            variants = ub.ddict(list)
            for hashmode in hashmodes_of_interest:
                for entry in entries:
                    if hashmode in entry['header']['name']:
                        variants[hashmode].append(entry)
            parsed[k] = variants

        rows = []
        for devname, variants in parsed.items():
            for hashmode, entries in variants.items():
                for entry in entries:
                    for test in entry['tests']:
                        rows.append({
                            'device': devname,
                            'hashmode': hashmode,
                            'full_hashmode': entry['header']['name'],
                            'test_num': test['test_num'],
                            'rate': test['rate'],
                        })
        import pandas as pd
        df = pd.DataFrame(rows)
        df = df.sort_values(['hashmode', 'full_hashmode'])
        import rich
        rich.print(df.to_string())

    hashmodes_3090 = [
            # {
            #     # This is actually the worst case (how fast to print to stdout)
            #     'hashmode': 'STDOUT',
            #     'notes': 'pathological',
            #     'attempts_per_second': 24549.4 * 1e9,
            # },

            {
                # A "Stronger" modern (2021) scheme
                'hashmode': 'VeraCrypt Streebog-512',
                'notes': 'strongest',
                'attempts_per_second': 46,
            },

            {
                'hashmode': 'HMAC-SHA256',
                'notes': 'weak',
                'attempts_per_second': 1898.6 * 1e6,
            },

            {
                'hashmode': 'sha256($pass.$salt)',
                'notes': 'weak',
                'attempts_per_second': 9746.6 * 1e6,
            },

            {
                # A "Weak" but still used scheme
                'hashmode': 'md5',
                'notes': 'weak',
                'attempts_per_second': 65079.1 * 1e6,
            },

            {
                # A "Good" modern (2021) scheme
                'hashmode': 'bcrypt $2*$, Blowfish',
                'notes': 'strong',
                'attempts_per_second': 96662,
            },

            {
                'hashmode': 'AES Crypt (SHA256), k=8191',
                'notes': 'good',
                'attempts_per_second': 922.9 * 1e3,
            },
            {
                # Based on rtx3090 attacking eth wallet
                # This is a standin for a reasonably secure password hashmode
                'hashmode': 'ETH-PBKDF2-HMAC-SHA256',
                'notes': 'good',
                'attempts_per_second': 3934 * 1e3,
            },
            {
                # A "Strong" modern (2021) scheme
                'hashmode': 'VeraCrypt SHA512 + XTS 512 bit',
                'notes': 'very strong',
                'attempts_per_second': 2837,
            },

            {
                # This is a reasonable worst-case password hashmode
                'hashmode': 'Plaintext',
                'notes': 'weakest',
                'attempts_per_second': 121 * 1e9,
            },
    ]

    hashmodes_4090 = [
            # {
            #     # This is actually the worst case (how fast to print to stdout)
            #     'hashmode': 'STDOUT',
            #     'notes': 'pathological',
            #     'attempts_per_second': 24549.4 * 1e9,
            # },

            {
                # A "Stronger" modern (2021) scheme
                # (VeraCrypt Streebog-512 + XTS 1536 bit) (Iterations: 499999)
                'hashmode': 'VeraCrypt Streebog-512',
                'notes': 'strongest',
                'attempts_per_second': 102,
            },

            {
                'hashmode': 'HMAC-SHA256',  # (HMAC-SHA256 (key = $pass))
                'notes': 'weak',
                'attempts_per_second': 4.333900e9,
            },

            {
                'hashmode': 'sha256($pass.$salt)',
                'notes': 'weak',
                'attempts_per_second': 2.196030e+10,
            },

            {
                # A "Weak" but still used scheme
                'hashmode': 'md5',
                'notes': 'weak',
                'attempts_per_second': 1.641000e+11,
            },

            {
                # A "Good" modern (2021) scheme
                'hashmode': 'bcrypt $2*$, Blowfish',
                'notes': 'strong',
                'attempts_per_second': 1.840000e+05,
            },

            {
                'hashmode': 'AES Crypt (SHA256), k=8191',
                'notes': 'good',
                'attempts_per_second': 2111.5 * 1e3,
            },
            {
                # Based on rtx3090 attacking eth wallet
                # This is a standin for a reasonably secure password hashmode
                'hashmode': 'ETH-PBKDF2-HMAC-SHA256',  # Ethereum Wallet, PBKDF2-HMAC-SHA256
                'notes': 'good',
                'attempts_per_second': 8341.3 * 1e3,
            },
            {
                # A "Strong" modern (2021) scheme
                'hashmode': 'VeraCrypt SHA512 + XTS 512 bit',
                'notes': 'very strong',
                'attempts_per_second': 6.432000e+03,
            },

            {
                # This is a reasonable worst-case password hashmode
                'hashmode': 'Plaintext',
                'notes': 'weakest',
                'attempts_per_second': 2.653000e+11,
            },
    ]

    chosen_hashmodes = []
    if MODE in {'full'}:
        chosen_hashmodes += [
            'VeraCrypt Streebog-512',
            'HMAC-SHA256',
            'sha256($pass.$salt)',
            'md5',
        ]

    if MODE in {'big', 'full'}:
        chosen_hashmodes.extend([
             'bcrypt $2*$, Blowfish',
        ])

    chosen_hashmodes.extend([
        'AES Crypt (SHA256), k=8191',
    ])

    if 1:
        chosen_hashmodes.extend([
            'ETH-PBKDF2-HMAC-SHA256',
            'VeraCrypt SHA512 + XTS 512 bit',
            'Plaintext',
        ])

    hashmodes_3090 = sorted(hashmodes_3090, key=lambda x: x['attempts_per_second'])
    hashmodes_4090 = sorted(hashmodes_4090, key=lambda x: x['attempts_per_second'])

    devices = [
        {
            'name': 'RTX_3090',
            # Note: it may be the case that a particular hashmode does not use
            # all of the available GPU wattage, so we should account for that
            # if we can.
            'watts': 370.0,
            'benchmarks': [d for d in hashmodes_3090 if d['hashmode'] in chosen_hashmodes],
        },
        {
            'name': 'RTX_4090',
            # Note: it may be the case that a particular hashmode does not use
            # all of the available GPU wattage, so we should account for that
            # if we can.
            'watts': 450.0,
            'benchmarks': [d for d in hashmodes_4090 if d['hashmode'] in chosen_hashmodes],
        }
    ]

    # Notes on watts.
    # https://en.wikipedia.org/wiki/Watt
    # A Watt is a unit of power, radiant flux, i.e. the rate of work or rate of
    # energy transfer.
    # 1 Watt = 1 kg * (meter ** 2) * (seconds ** -3) = 1 Joule / second

    # A Type1 Civilization could use energy at a rate of 1.74e18 watts
    type_1_watts = 1.74e17
    type_1_watts / 350

    # Enumerate theoretical scales to bound how many devices a threat actor
    # might have

    scales = []

    if MODE in {'full'}:
        scales += [
            {'name': 'Randos1000',     'num_devices': 1e3},    # 1,000.
            {'name': 'LargeCity',      'num_devices': 1e6},    # 1 million
            {'name': 'Metropolis',     'num_devices': 10e6},   # 10 million
            {'name': 'SmallNation',    'num_devices': 100e6},  # 100 million
            {'name': 'LargeNation',    'num_devices': 1e9},    # 1 billion
            # 'Austin_2020': 1e6,  # about 1 million.
            # 'NYC_2019': 8.419e6,  # 8 million
            # 'GPU_Shipments_2020': 41e6,  # 46 million
            # 'USA_2019': 328.2e6,     # 300 million
            # 'China_2021': 1_397_897_720,  # 1 billion
            # 'Earth_2019': 7.674e9,  # 7 billion
        ]

    if MODE in {'full', 'big'}:
        scales += [
            {'name': 'Randos',         'num_devices': 1e0},    # exactly 1.
            {'name': 'Randos100',      'num_devices': 100e0},  # 100.
        ]

    scales += [
        {'name': 'SmallCity',      'num_devices': 100e3},  # 100,000
        {'name': 'Type0.73-World', 'num_devices': 10e9},   # 10 billion
        {'name': 'Type1-World',    'num_devices': 10e14},  # Distant Future (maybe, it's up to us)
    ]

    scales = sorted(scales, key=lambda x: x['num_devices'])

    # For our idealized purpose we will ignore the "zipties and baseball bat"
    # hacker device... because somebody is going to bring it up otherwise
    return devices, scales


def humanize_seconds(seconds, colored=True, precision=4, named=False):
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
    count_ = round(float(count), 4)
    if named:
        ret = '{} {}'.format(named_large_number(count), unit)
    else:
        ret = ('{:.' + str(precision) + 'g} {}').format(count_, unit)

    if colored:
        if years > 1e5:
            # Blue is VERY safe
            ret = ub.color_text(ret, 'blue')
        elif years > 80:
            # Green is safe
            ret = ub.color_text(ret, 'green')
        elif years > 10:
            # Yellow is short-term safe
            ret = ub.color_text(ret, 'yellow')
        else:
            # Red is not safe
            ret = ub.color_text(ret, 'red')
    return ret


def humanize_dollars(dollars, named=False, colored=False):
    if named:
        text = '${}'.format(named_large_number(dollars))
        # return '${:5.02g}'.format(float(dollars))
    else:
        text = '${:5.02g}'.format(float(dollars))
    if colored:
        if dollars > 1e16:
            # Blue is VERY safe
            text = ub.color_text(text, 'blue')
        elif dollars > 1e6:
            # Green is safe
            text = ub.color_text(text, 'green')
        elif dollars > 1e3:
            # Yellow is short-term safe
            text = ub.color_text(text, 'yellow')
        else:
            # Red is not safe
            text = ub.color_text(text, 'red')
    return text


def named_large_number(num, prefix='auto', precision=2):
    """
    https://en.wikipedia.org/wiki/Names_of_large_numbers

    Example:
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc/notes'))
        >>> from password_model import *  # NOQA
        >>> import random
        >>> rng = random.Random(0)
        >>> lines = []
        >>> test_mags = (list(range(-10, 3 * 22)) + [3 * 100, 3 * 101, 3 * 102])
        >>> # test_mags = list(range(-1, 3 * 5))
        >>> for mag in test_mags:
        >>>     coef = rng.random()
        >>>     for coef in [1.0, 1.1]:
        >>>         num = coef * (10 ** mag)
        >>>         text = named_large_number(num)
        >>>         line = 'text@{:3d}: {}'.format(mag, text)
        >>>         lines.append(line)
        >>> print('lines = {}'.format(ub.repr2(lines, nl=1), align=' '))
    """
    magnitude_to_prefix = {
        3 *  0: '',
        3 *  1: 'thousand',
        3 *  2: 'million',
        3 *  3: 'billion',
        3 *  4: 'trillion',
        3 *  5: 'quadrillion',
        3 *  6: 'quintillion',
        3 *  7: 'sextillion',
        3 *  8: 'septillion',
        3 *  9: 'octillion',
        3 * 10: 'nonillion',
        3 * 11: 'decillion',
        3 * 12: 'undecillion',
        3 * 13: 'duodectillion',
        3 * 14: 'tredecillion',
        3 * 15: 'quattuor-decillion',
        3 * 16: 'quindecillion',
        3 * 17: 'sexdecillion',
        3 * 18: 'septendecillion',
        3 * 19: 'octodecillion',
        3 * 20: 'novemdecillion',
        3 * 21: 'vigintillion',
        3 * 101: 'centillion',
    }
    prefix_to_magintude = ub.invert_dict(magnitude_to_prefix)

    num_mag = math.log(abs(float(num) + 1), 10)
    if prefix == 'auto':
        chosen_prefix = ''
        for cand_mag, cand_prefix in magnitude_to_prefix.items():
            if num_mag >= (cand_mag):
                chosen_prefix = cand_prefix
        prefix = chosen_prefix
    mag = prefix_to_magintude[prefix]

    coeff = num / (10 ** mag)
    coef_repr = ub.repr2(float(coeff), precision=precision)
    text = coef_repr + ' ' + prefix
    return text


def monkeypatch_pandas_colored_stdout():
    """
    References:
        https://github.com/pandas-dev/pandas/issues/18066
    """
    import pandas.io.formats.format as format_
    from six import text_type

    # Made wrt pd.__version__ == '1.2.4'

    class TextAdjustmentMonkey(object):
        def __init__(self):
            import re
            self.ansi_regx = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
            self.encoding  = format_.get_option("display.encoding")

        def len(self, text):
            return len(self.ansi_regx.sub('', text))

        def justify(self, texts, max_len, mode='right'):
            jfunc = str.ljust if (mode == 'left')  else \
                    str.rjust if (mode == 'right') else str.center
            out = []
            for s in texts:
                escapes = self.ansi_regx.findall(s)
                if len(escapes) == 2:
                    out.append(escapes[0].strip() +
                               jfunc(self.ansi_regx.sub('', s), max_len) +
                               escapes[1].strip())
                else:
                    out.append(jfunc(s, max_len))
            return out

        def _join_unicode(self, lines, sep=''):
            try:
                return sep.join(lines)
            except UnicodeDecodeError:
                sep = text_type(sep)
                return sep.join([x.decode('utf-8') if isinstance(x, str) else x
                                                                for x in lines])

        def adjoin(self, space, *lists, **kwargs):
            # Add space for all but the last column:
            pads = ([space] * (len(lists) - 1)) + [0]
            max_col_len = max([len(col) for col in lists])
            new_cols = []
            for col, pad in zip(lists, pads):
                width = max([self.len(s) for s in col]) + pad
                c     = self.justify(col, width, mode='left')
                # Add blank cells to end of col if needed for different col lens:
                if len(col) < max_col_len:
                    c.extend([' ' * width] * (max_col_len - len(col)))
                new_cols.append(c)

            rows = [self._join_unicode(row_tup) for row_tup in zip(*new_cols)]
            return self._join_unicode(rows, sep='\n')

    format_.TextAdjustment = TextAdjustmentMonkey


def main():
    """
    Run password security analysis

    Example:
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc/notes'))
        >>> from password_model import *  # NOQA
        >>> main()
    """
    import itertools as it
    from fractions import Fraction
    import pandas as pd
    # Build our adversary and our strategies
    devices, scales = build_threat_models()

    password_schemes = build_password_strategy()

    # Other estimates or assumptions
    estimates = {
        # estimated cost of using a kilowatt for an hour
        # http://www.wrecc.com/what-uses-watts-in-your-home/
        # https://www.coinwarz.com/mining/ethereum/calculator

        'dollars_per_kwh': 0.10,
    }

    rows = []
    for device_info, scheme, scale in it.product(devices, password_schemes, scales):
        for benchmark in device_info['benchmarks']:

            states = Fraction(scheme['states'])
            num_devices = Fraction(scale['num_devices'])
            dollars_per_kwh = Fraction(estimates['dollars_per_kwh'])

            hashmode_attempts_per_second = benchmark['attempts_per_second']
            attempts_per_second = num_devices * Fraction(int(hashmode_attempts_per_second))

            seconds = states / Fraction(attempts_per_second)

            hours = seconds / Fraction(3600)
            device_kilowatts = Fraction(device_info['watts']) / Fraction(1000)
            device_dollars_per_hour = device_kilowatts * dollars_per_kwh
            dollars_per_device = device_dollars_per_hour * hours
            dollars = dollars_per_device * num_devices

            total_kilowatts = device_kilowatts * num_devices * hours

            row = {
                'scheme': scheme['name'],
                'entropy': scheme['entropy'],

                'hashmode': benchmark['hashmode'],
                'hashmode_attempts_per_second': int(hashmode_attempts_per_second),

                'device': device_info['name'],
                'scale': scale['name'],
                'num_devices': scale['num_devices'],

                'seconds': seconds,
                'dollars': dollars,

                'kilowatts': total_kilowatts,
                'hours': hours,
                'dollars_per_kwh': estimates['dollars_per_kwh'],
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values('entropy')

    # device = 'RTX_3090'
    device = ub.argval('--device', 'RTX_4090')
    df = df[df['device'] == device]
    df['time'] = df['seconds'].apply(humanize_seconds)
    df['cost'] = df['dollars'].apply(partial(humanize_dollars, colored=1))
    df['entropy'] = df['entropy'].round(2)
    df['num_devices'] = df['num_devices'].apply(int)

    hashmodes = sorted([d['hashmode'] for d in device_info['benchmarks']])

    # https://github.com/pandas-dev/pandas/issues/18066
    monkeypatch_pandas_colored_stdout()

    # Output our assumptions
    print('\n---')
    print('Assumptions:')
    device_info = ub.group_items(devices, lambda x: x['name'])[device][0]
    print('estimates = {!r}'.format(estimates))
    print('device_info = {}'.format(ub.repr2(device_info, nl=2)))

    # For each hashmode, print the scheme-vs-num_devices-vs-time matrix
    hashmode_to_pivots = {}
    for hashmode in hashmodes:
        subdf = df
        subdf = subdf[subdf['hashmode'] == hashmode]
        subdf = subdf.sort_values(['entropy', 'num_devices'])
        piv = subdf.pivot(['entropy', 'cost', 'scheme'], ['num_devices', 'scale'], 'time')
        # piv.style.applymap(color_cases)
        hashmode_to_pivots[hashmode] = piv

    for hashmode in hashmodes:
        print('\n---')
        print('hashmode = {!r}'.format(hashmode))
        piv = hashmode_to_pivots[hashmode]
        print(piv)

    # Print the scheme-vs-hashmode-vs-cost matrix
    print('\n---')
    print('Cost Matrix:')
    subdf = df[df['scale'] == df['scale'].iloc[0]]
    piv = subdf.pivot(['entropy', 'scheme'], ['hashmode_attempts_per_second', 'hashmode'], 'cost')
    piv = piv.sort_index(axis=1, ascending=False)
    piv.columns = piv.columns.droplevel(0)
    print(piv)

    # Make the visualizations
    if ub.argflag('--show'):
        import kwplot
        from matplotlib.colors import LogNorm
        import matplotlib as mpl
        plt = kwplot.autoplt()
        sns = kwplot.autosns()

        use_latex = ub.argflag('--latex')
        if use_latex:
            mpl.rcParams['text.usetex'] = True

        def time_labelize(x):
            text = humanize_seconds(x, colored=False, named=True, precision=2)
            parts = text.split(' ')
            if use_latex:
                text = r'{\huge ' + parts[0] + '}' + '\n' + ' '.join(parts[1:])
            else:
                text = parts[0] + '\n' + ' '.join(parts[1:])
            return text

        def dollar_labelize(dollars):
            cost = humanize_dollars(dollars, named=(dollars > 1))
            if use_latex:
                cost = cost.replace('$', r'\$')
            return cost

        hashmode_to_notes = {}
        for dev in devices[0]['benchmarks']:
            hashmode_to_notes[dev['hashmode']] = dev['notes']

        if 1:
            # Independent of the adversary scale we can plot cost versus scheme
            # cost vs hashmod?
            subdf = df[df['scale'] == df['scale'].iloc[0]]
            piv = subdf.pivot(['entropy', 'scheme'],
                              ['hashmode_attempts_per_second', 'hashmode'],
                              'dollars')
            piv = piv.sort_index(axis=1, ascending=False)

            # https://stackoverflow.com/questions/64234474/cust-y-lbls-seaborn
            ax: mpl.axes.Axes = plt.subplots(figsize=(20 * 1.2, 10 * 1.2))[1]

            annot = piv.applymap(dollar_labelize)
            piv = piv.applymap(float)

            sns.heatmap(piv, annot=annot, ax=ax, fmt='s',
                        norm=LogNorm(vmin=1, vmax=100_000_000_000_000_000),
                        annot_kws={'size': 16},
                        cmap='cividis',
                        cbar_kws={'label': 'dollars', 'pad': 0.001})

            # Find colorbar
            for subax in ax.figure.axes:
                if subax.get_label() == '<colorbar>':
                    subax.set_ylabel('dollars', labelpad=0)
                    break

            new_ytick_labels = []
            for ent, scheme in piv.index.to_list():
                if use_latex:
                    scheme = r'{\LARGE ' + scheme + '}'
                _ = '{scheme}\nEntropy={ent}bits'.format(scheme=scheme, ent=ent)
                new_ytick_labels.append(_)

            new_xtick_labels = []
            for _, hashmode in piv.columns.to_list():
                notes = ''
                if hashmode in hashmode_to_notes:
                    notes = '\n(' + hashmode_to_notes[hashmode] + ')'
                new_xtick_labels.append(hashmode + notes)

            ax.set_xticklabels(new_xtick_labels, rotation=0)
            ax.set_yticklabels(new_ytick_labels, rotation=0)

            ax.set_ylabel('Password Scheme, Entropy', labelpad=24)
            ax.set_xlabel('Hashmode', labelpad=16)

            if use_latex:
                title = f'{{\\Huge Password Cost Security: {device}}}'
                ax.set_title(title)
            else:
                ax.set_title(f'Password Cost Security: {device}')

            ax.figure.subplots_adjust(
                # bottom=0.1, left=0.20, right=1.0, top=0.90, wspace=0.001)
                bottom=0.1, left=0.10, right=1.0, top=0.90, wspace=0.001)

            if ub.argflag('--save'):
                fname = f'passwd_cost_security_{device}.png'
                print(f'Save: {fname}')
                ax.figure.savefig(fname)
                try:
                    import kwplot
                    cropwhite_ondisk(fname)
                except Exception:
                    ...

        if 0:
            # For each hashmode plot (scheme versus adversary scale)
            for hashmode in ub.ProgIter(hashmodes, desc='plotting'):
                subdf = df
                subdf = subdf[subdf['hashmode'] == hashmode]
                subdf = subdf.sort_values(['entropy', 'num_devices'])

                piv = subdf.pivot(
                    ['entropy', 'dollars', 'scheme'],
                    ['num_devices', 'scale'],
                    'seconds')
                piv = piv.applymap(float)

                # https://stackoverflow.com/questions/64234474/cust-y-lbls-seaborn
                # ax: mpl.axes.Axes = plt.subplots(figsize=(15, 10))[1]
                ax: mpl.axes.Axes = plt.subplots(figsize=(15 * 1.2, 10 * 1.2))[1]

                annot = piv.applymap(time_labelize)
                sns.heatmap(piv, annot=annot, ax=ax, fmt='s',
                            norm=LogNorm(vmin=1, vmax=8640000000),
                            annot_kws={'size': 10},
                            cbar_kws={'label': 'seconds', 'pad': 0.001})

                # Find colorbar
                for subax in ax.figure.axes:
                    if subax.get_label() == '<colorbar>':
                        subax.set_ylabel('seconds', labelpad=0)
                        break

                new_ytick_labels = []
                for ent, dollars, scheme in piv.index.to_list():
                    cost = dollar_labelize(dollars)
                    if use_latex:
                        scheme = r'{\LARGE ' + scheme + '}'
                    _ = '{scheme}\nEntropy={ent}bits\nCost={cost}'.format(scheme=scheme, cost=cost, ent=ent)
                    new_ytick_labels.append(_)

                new_xtick_labels = []
                for n, name in piv.columns.to_list():
                    if use_latex:
                        name = r'{\LARGE ' + name + '}'
                    _ = name + '\n' + named_large_number(n, precision=0) + ' GPUs'
                    new_xtick_labels.append(_)

                ax.set_xticklabels(new_xtick_labels, rotation=0)
                # ax.set_yticklabels(new_ytick_labels, horizontalalignment='left', pad=30)
                ax.set_yticklabels(new_ytick_labels)

                ax.set_ylabel('Password Scheme, Entropy, and Cost to Crack', labelpad=24)
                ax.set_xlabel('Adversary Resources', labelpad=16)

                notes = ''
                if hashmode in hashmode_to_notes:
                    notes = ' (' + hashmode_to_notes[hashmode] + ')'

                if use_latex:
                    title = f'{{\\Huge Password Time Security: {device}}}\nhashmode={hashmode}{notes}'
                    ax.set_title(title)
                else:
                    ax.set_title(f'Password Time Security: {device}\n(hashmode={hashmode}{notes})')

                ax.figure.subplots_adjust(
                    bottom=0.1, left=0.20, right=1.0, top=0.90, wspace=0.001)

                if ub.argflag('--save'):
                    fname = f'passwd_robustness_{hashmode}_{device}.png'
                    print(f'Save: {fname}')
                    ax.figure.savefig(fname)
        plt.show()


def cropwhite_ondisk(fpath):
    import kwimage
    from kwplot.mpl_make import crop_border_by_color
    imdata = kwimage.imread(fpath)
    imdata = crop_border_by_color(imdata)
    kwimage.imwrite(fpath, imdata)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/notes/password_model.py --device=RTX_3090 --save --show
        python ~/misc/notes/password_model.py --device=RTX_4090 --save --show

        python ~/misc/notes/password_model.py --show
        python ~/misc/notes/password_model.py --show --MODE=small
    """
    main()
