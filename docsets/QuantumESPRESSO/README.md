# Quantum ESPRESSO

This docset is generated for [Quantum ESPRESSO](https://www.quantum-espresso.org) (QE), an open-source package for electronic-structure calculations and materials modeling at the nanoscale. It is maintained by Chenxing Luo ([chazeon](https://github.com/chazeon)), it was generated based on the QE's official documents that is generated from its source code.

The docset generation script and corresponding generation guide is open-sourced at the [QE Docset](https://github.com/chazeon/qe-docset) repo, briefly speaking, it includes:
* Download the official source code
  * Generate the official document by running `configure` and `make doc` to generate the documents from the source code
* Clone the generation script from [QE Docset](https://github.com/chazeon/qe-docset) repo and
  * Install the dependencies by running `pip3 install -r requirements.txt` from the scripts directory.
  * Edit the `generation.sh` and run it

To build docsets in batch for various versions of QE, you can refer to the [auto build scripts](https://github.com/chazeon/qe-docset-autobuild).

Also, a website about it has been hosted on the [GitHub Pages](https://chazeon.github.io/qe-docset/), where you can download the archives of the docsets directly. If you are interested go take a look!