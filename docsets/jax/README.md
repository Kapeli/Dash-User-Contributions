JAX
=======================

About
-----
[JAX](https://jax.readthedocs.io/en/latest/) is NumPy on the CPU, GPU, and TPU, with great automatic differentiation for high-performance machine learning research.

Versions
- Version 0.1.67 generated on 05-09-20 ([@nirum](https://github.com/nirum)).

Instructions on how to generate the docset
------------------------------------------
1. Install [doc2dash](https://doc2dash.readthedocs.io/).
2. Clone [JAX](https://github.com/google/jax/).
3. [Build the documentation](https://jax.readthedocs.io/en/latest/developer.html#update-documentation).
4. Run `doc2dash -A --online-redirect-url https://jax.readthedocs.io/ --name jax docs/build/html` to generate the docset.
