# Math Facts

This document contains notes where if I learn a math thing, I'll write it down
here to help me remember it better.


* A infinitely differentiable function is Morse if its critical points (points with 0 linear gradient) have non-singular a Hessian matrix (i.e. is non-degenerate). (https://arxiv.org/pdf/2307.15744)


* Fubini's theorem lets you evaluate a double integral as two single integrals if the integrand is measurable the double integral absolutely finite (i.e. finite in a stronger sense than having an infinite number of cancellations). 

```

∬_{X × Y) f(x, y) d(x, y) =

∫_X ( ∫_Y f(x, y) dy) dx = 

∫_Y ( ∫_X f(x, y) dx) dy  

```

only if `f` is measurable and

`∬_{X × Y) |f(x, y)| d(x, y) < ∞`


* The Frank-Wolfe algorithm is an iterative way to find a solution a constrained CONVEX optimization problem (using first order gradient methods). Differs from gradient descent in that you need to know the shape of the loss surface and move along it directly. GD takes a step in an arbitrary direction and then projects onto the surface. 



* A Vandermonde matrix is an MxN matrix where each row is a geometric progression. In other words, for the i-th row there is a variable x[i], and the
columns are `[x[i] ** j for j in range(n)]`, or in other words, each cell is `V[i, j] = x[i] ** j`.


* The minor of an element in a matrix is the determinant of the smaller submatrix created by removing that element's row and column.


-----

Need to learn:

What is the minor of a matrix. 

What is an ideal of an image (inverse?)

Oh, the image of the network is the output.


All ideals are finitely generated, but what those might be is unclear.

Ideals are the analogue of normal subgroups


all such quartic polynomials are invariants in the ideal of the model.
