Neural Tangent Kernel
---------------------

Last time I was in the office I was working on understanding a paper about the Neural Tangent Kernel. I've spent many nights going through the math, and while I don't think I understand it well enough to teach it, I am converging towards that. I wanted to post some useful resources I found about it, as well an interesting practical takeaway.

One of the key points in the paper is highlighting a surprising empirical observation and building the theory to attempt to understand it. The observation is: 

As networks get wider, the difference in the random initialization of the parameters, and the parameters after training has converged is very small. 

I was not aware of this empirical result, and I find it surprising. Something I added yesterday to the geowatch trainer is an option that saves the initialization weights of the network before learning starts, which I plan to use to see if I can observe this practical applications.

Linked are the paper, a wiki article, two blog posts that I found much more helpful than the paper itself, and a the best of the youtube lectures I found explaining it: 


https://arxiv.org/pdf/1806.07572

https://en.wikipedia.org/wiki/Neural_tangent_kernel

https://lilianweng.github.io/posts/2022-09-08-ntk/

https://www.borealisai.com/research-blogs/the-neural-tangent-kernel/

https://www.youtube.com/watch?v=DObobAnELkU

* when neural networks become very wide, their parameters do not change much during training and they can be considered as approximately linear

     + This makes sense because you can always rewrite a separable non-linear function as a linear function in higher dimensions [ref: https://stats.stackexchange.com/questions/479817/will-non-linear-data-always-become-linear-in-high-dimension]
