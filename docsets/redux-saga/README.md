redux-saga Docset
=======================

- __Docset Description__:
	- [redux-saga](https://redux-saga.js.org/) is a library that aims to make application side effects (i.e. asynchronous things like data fetching and impure things like accessing the browser cache) easier to manage, more efficient to execute, easy to test, and better at handling failures.

- __Author__: 
	- [Dmitry Tutykhin](https://github.com/dmitrytut)

- __Docset Repo__: 
	- [redux-saga-docset](https://github.com/dmitrytut/redux-saga-docset)

- __Instructions__:
	``` bash
    # Install go. On MacOS execute...
    ~ brew install go
    # Install Dashing.
    ~ go get -u github.com/technosophos/dashing
    # Clone files for Docset.
    ~ git clone git@github.com:dmitrytut/redux-saga-docset.git
    # Change into folder.
    ~ cd redux-saga-docset/docs
    # Edit dashing.json or leave the defaults. (For further information please visit https://github.com/technosophos/dashing).
    ~ vim dashing.json
    # Start generation (depending on the install path of Dashing).
    ~ ~/go/bin/dashing build redux-saga
    ```
    
    After generation, you can import the docset into the Dash app.