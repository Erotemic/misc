import pint
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


(1 * reg.joule / (reg.volt * reg.seconds)).to_base_units()
(1 * reg.watt / reg.volt).to_base_units()
(1 * reg.amp).to_base_units()


simplify(quantity)


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
