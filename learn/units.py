import pint
import ubelt as ub
reg = pint.UnitRegistry()

lut = {}
for unit_name in list(reg):
    unit = getattr(reg, unit_name, None)
    if unit is not None:
        q = 1 * unit
        base = q.to_base_units()
        base.units
        lut[unit_name] = base.units

rlut = ub.invert_dict(lut, unique_vals=0)


def simplify(quantity):
    print(rlut[quantity.units])


# https://en.wikipedia.org/wiki/Joule
(1 * reg.joule / (reg.volt * reg.seconds)).to_base_units()
(1 * reg.watt / reg.volt).to_base_units()
(1 * reg.amp).to_base_units()

(1 * reg.watt).to_base_units()

# Tripp Lite Isobar 10
val = 3840 * reg.joule

(val / reg.amp).to_base_units()

(val / (1800 * reg.watt)).to_base_units()

units = [
    reg.watt,
    reg.amp,
    reg.volt,
    reg.joule,
]

quantities = [1 * u for u in units]

for quantity in quantities:
    base = quantity.to_base_units()
    print('{:>10} = {}'.format(str(quantity), base))
    simplify(quantity / reg.amp)

(1 * reg.amp).to_base_units()

(1 * reg.ohm).to_base_units()
(1 * reg.watt).to_base_units()

(1 * reg.volt).to_base_units()
(1 * reg.joule).to_base_units()

(1 * reg.volt * reg.amp * reg.second).to_base_units()

(1 * (reg.joule / reg.watt)).to_base_units()

(1 * (reg.joule / reg.amp)).to_base_units().to_compact()
z = (1 * (reg.joule / reg.amp)).to_base_units()
z.to_compact()

(1 * (reg.joule / reg.amp)).to_reduced_units()


# volt * amp = watt

# Example with numbers from a portable battery
class Battery:
    def __init__(self, volts=None, amps=None, watts=None, amp_hours=None, watt_hours=None):
        self.volts = volts
        self.amps = amps
        self.watts = watts
        self.amp_hours = amp_hours
        self.watt_hours = watt_hours
        self.infer = ub.ddict(ub.oset)

    def print_specs(self):
        print(f'self.volts={self.volts}')
        print(f'self.amps={self.amps}')
        print(f'self.watts={self.watts}')
        print(f'self.amp_hours={self.amp_hours}')
        print(f'self.watt_hours={self.watt_hours}')
        print('self.infer = {}'.format(ub.repr2(self.infer, nl=1)))

    def solve(self):
        if self.watts is not None:
            self.infer['watts'].add(self.watts)
        if self.volts is not None:
            self.infer['volts'].add(self.volts)
        if self.amps is not None:
            self.infer['amps'].add(self.amps)
        if self.watt_hours is not None:
            self.infer['watt_hours'].add(self.watt_hours)
        if self.amp_hours is not None:
            self.infer['amp_hours'].add(self.amp_hours)

        for i in range(4):
            import itertools as it
            for w, a in it.product(ub.oset(self.infer['watts']), ub.oset(self.infer['amps'])):
                self.infer['volts'].add((w / a).to(reg.volts))

            for w, v in it.product(ub.oset(self.infer['watts']), ub.oset(self.infer['volts'])):
                self.infer['amps'].add((w / v).to(reg.ampere))

            for a, v in it.product(ub.oset(self.infer['amps']), ub.oset(self.infer['volts'])):
                self.infer['watts'].add((a * v).to(reg.watts))

            for wh, ah in it.product(ub.oset(self.infer['watt_hours']), ub.oset(self.infer['amp_hours'])):
                self.infer['volts'].add((wh / ah).to(reg.volts))


watt_hours = 39.52 * reg.watt_hour
amp_hours = (10400 / 1e3) * reg.ampere_hour
# voltage = 12 * reg.volts
# amps = 1.5 * reg.ampere
voltage = (watt_hours / amp_hours).to(reg.volts)
voltage = 5 * reg.volts
amps = 3 * reg.ampere
# self = Battery(volts=voltage, amps=amps, amp_hours=amp_hours, watt_hours=watt_hours)
self = Battery(volts=voltage, amps=amps, amp_hours=amp_hours, watt_hours=watt_hours)
self.solve()
self.print_specs()
