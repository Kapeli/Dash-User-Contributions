Solidity Docset
=======================

> ###Latest 0.4.21

Solidity docset for Dash 

- __Docset Description__:
	- [Solidity](solidity.readthedocs.io) is contract-oriented, high-level, programming language for implementing smart contracts. Influenced by C++, Python and Javascript. Designed to target the Ethereum Virtual Machine

- __Author__: 
	- [Oscar Chavez <oschvr>](http://github.com/oschvr)

- __Docset Repo__: 
	- [solidity-dash](https://github.com/oschvr/solidity-dash)

- __Instructions__:
	-  Clone the repo and cd into it
	- Executing `bash setup.sh` will:
		- Try to install dependencies (see repo)
		- Fetch the **ethereum** repo
		- Go to docs dir and make them into html
		- Copy them to **solidity.docset**
		- Copy info.plist, dsidx and icon.svg into **solidity.docset**
		- Run `populate.py` to iterate through the htmls and fill the db. 
