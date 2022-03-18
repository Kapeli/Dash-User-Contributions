Chassis Docset
==============

This is the Dash docset for [Chassis](http://docs.chassis.io/en/latest/) an open source virtual server for your WordPress site, built using Vagrant.

Authors:
* Bronson Quick
   * [Github](https://github.com/BronsonQuick/)
   * [Website](https://www.bronsonquick.com.au/)
* Ryan McCue
   * [Github](https://github.com/rmccue/)
   * [Website](https://rmccue.io/)
   * [Twitter](https://twitter.com/rmccue/)

### Building Offline Dash Documentation

We use [doc2dash](https://doc2dash.readthedocs.io/en/stable/) to generate offline documentation for [Dash](https://kapeli.com/dash).
If you wish to generate new documentation for Chassis then please to the following:

1. Clone the Chassis repository. `git clone --recursive https://github.com/Chassis/Chassis.git <your-folder>`.
1. `cd <your-folder>`.
1. Run `pip install --user doc2dash`
1. Increase the [version number](https://github.com/Chassis/Chassis/blob/master/docs/conf.py#L57-L59) to match the release.
1. Run `make html` inside the `docs` folder.
1. Run `doc2dash -A _build/dirhtml/ -n Chassis -f -I index.html` to generate the new docset.
1. Follow the instructions for the [Dash User Contributed Docsets](https://github.com/Chassis/Dash-User-Contributions.git) repository and submit a pull request.

