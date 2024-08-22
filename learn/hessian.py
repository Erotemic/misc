"""
https://stackoverflow.com/questions/31206443/numpy-second-derivative-of-a-ndimensional-array
https://pytorch.org/docs/stable/generated/torch.autograd.functional.hessian.html
https://pytorch.org/docs/stable/generated/torch.autograd.functional.jacobian.html
https://carmencincotti.com/2022-08-15/the-jacobian-vs-the-hessian-vs-the-gradient/
"""
import sympy as sp
sp.init_printing()

x_i, y_i = sp.symbols("x_i,y_i")
f = sp.Function("f")(x_i, y_i)
f = (1 - sp.exp(-10 * x_i ** 2 - y_i ** 2)) / 100


# Jacobian matrix - first derivative
J = sp.Matrix([f]).jacobian([x_i, y_i])
J

# Hessian matrix - second derivative
H = sp.hessian(f, (x_i, y_i))
H

import torch

network = torch.nn.Sequential(*[
    torch.nn.Linear(3, 5),
    torch.nn.ReLU(),
    torch.nn.Linear(5, 7),
    torch.nn.ReLU(),
    torch.nn.Linear(7, 1),
])

data = torch.rand(1, 3)
outputs = network(data)

J = torch.autograd.functional.jacobian(network.forward, data)
print(f'J.shape={J.shape}')
H = torch.autograd.functional.hessian(network.forward, data)
