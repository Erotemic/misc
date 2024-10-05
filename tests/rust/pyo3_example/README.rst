
.. code:: bash

    # https://github.com/rust-github/template/blob/main/template/Cargo.toml
    # https://doc.rust-lang.org/book/ch01-03-hello-cargo.html
    # https://pyo3.rs/main/getting-started
    pip install maturin
    cd ~/misc/tests/rust/pyo3_example
    maturin develop

    python -c "
    import pyo3_example
    import numpy as np
    print(repr(pyo3_example.sum_as_string(5, 20)))

    A = np.random.rand(5, 5)
    B = np.random.rand(5, 5)
    "

