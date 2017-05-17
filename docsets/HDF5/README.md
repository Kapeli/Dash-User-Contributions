# HDF5

Author: Patrick Widener (https://pwidene.github.io, twitter.com/agentplaid)

## How to generate this docset

### Mirror the HTML docs

The HDF5 Reference Manual is available at
https://support.hdfgroup.org/HDF5/doc/RM/RM_H5Front.html. The HDF5
Group doesn't provide a downloadable form of their API documentation,
so I use httrack (https://www.httrack.com, available in most Linux
repos and via MacPorts/Homebrew on macOS) to crawl the website to
retrieve the files. The saved mirror of the reference manual subtree
gets saved under the Documents folder by httrack as follows:

```
httrack https://support.hdfgroup.org/HDF5/doc/RM/ -O <path to
Documents>
```

### Generate the index

The Python script `hdf5docset.py` generates the sqlite3 index. This
script is a shameless near-copy of the one used by github.com/drbraden
to generate his PostgreSQL Dash docset
(https://github.com/drbraden/pgdash). The paths in this script expect
that the above httrack invocation was done as specified. The script will
generate a docSet.dsidx for the subset of the HDF5 docs contained in
the script's `apis` list.

## Issues

File issues/requests against the github repo for this docset at
https://github.com/pwidene/dash-hdf5.

