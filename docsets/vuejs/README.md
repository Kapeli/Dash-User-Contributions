Vue.js Docset
=======================

Prepared by [Chase Colman](https://github.com/chase)  
Twitter: [@Chase_the_Dev](https://twitter.com/Chase_the_Dev)

## Generating the Docset
### Prequisites
* Git ~v1.8
* Node.js ~v0.10
* NPM ~v1.3
* A functioning internet connection

### Downloading
`git clone --recursive https://github.com/chase/vue-dash-generator.git && npm install`

### Updating
1. `cd vue-dash-generator`
2. `git pull --recurse-submodules && git submodule update && npm install`

### Generating
1. `cd vue-dash-generator`
2. `gulp`

The raw docset can be found under the `build` directory as `vuejs.docset`

## Publishing the Docset
1. `cd vue-dash-generator`
2. *Assuming you already generated the docs:* `gulp publish`
3. `cd build/Dash-User-Contributions/docsets/vuejs'
4. Update the version in `docset.json
5. `git add *`
6. `git commit -m 'Import Docset archives for Vue.js vX.X.X'`  
*Obviously, you should replace the vX.X.X with the actual version above*
7. `git push`
