Nitrogen Docset
=======================

## Description

Nitrogen is a web framework for Erlang projects.

## Authors

* [Nitrogen Web Framework for Erlang](https://github.com/nitrogen) (Nitrogen
  Documentation)
  
* [Bunny Lushington](https://github.com/bunnylushington) (Dash Documentation Generator)

## Generating the Docset

### Requirements

* Erlang v23.0 or greater
* SQLite
* Docker

### Steps

* Clone [nitrogen_core](https://github.com/nitrogen/nitrogen_core)
  into the same parent directory as the Dash-User-Contributions
  repository.
  
* `cd nitrogen_core && make dash`

* `cp nitrogen_core/doc/dash/Nitrogen.tgz Dash-User-Contributions/docsets/Nitrogen`

* `cp nitrogen_core/doc/dash/icon.png Dash-User-Contributions/docsets/Nitrogen`

* Update the version number in docset.json.





## Caveats

The Nitrogen categories "Action" and "Validator" do not have Dash
counterparts; for the time being these have been categorized as
"Event" and "Test" respectively.
