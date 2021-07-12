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

