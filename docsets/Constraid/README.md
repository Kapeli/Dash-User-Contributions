# Constraid Docset

This is the **official** Dash Docset for the [Constraid][constraid] Swift framework.

## Who am I?

My name is Andrew (a.k.a. Drew) De Ponte. I am the official maintainer of the [Constraid][constraid] Swift framework. My social profiles are as follows:

- **GitHub:** [@cyphactor][github]
- **Twitter:** [@cyphactor][twitter]

Please don't hesitate to reach out.

## Docset Generation

### Prerequisits

In order to generate the docset you need to have the following:

- the latest version of XCode installed and setup
- the latest version of [Jazzy][jazzy] installed

### How to Generate

[Jazzy](https://github.com/realm/jazzy) makes it very easy to generate the docset. Simply do the following:

1. Clone the [Constraid]() git repository
2. Check out the tag version number (ex: 2.0.2) you want to generate the docset for
3. Run `jazzy -c -a "UpTech Works, LLC" -u http://upte.ch -m Constraid --module-version 2.0.2` at the root of the repository, without any options
4. Open `index` in your favorite SQLite3 editor and make sure there are no NULL type entries in the index, if there are correct them with appropriate types from [Dash Offical Types](https://kapeli.com/docsets#supportedentrytypes). *Note:* The ones that seem to be missing types are the top level sections in the index, Global Variables, Enumerations, Extensions, Functions, and Type Aliases, so I have been assigning the `Section` type to them.
5. Replace the [Jazzy][jazzy] generated `tgz` by removing it and creating a new one by running, `tar --exclude='.DS_Store' -cvzf Constraid.tgz Constraid.docset`

This will generate all the documentation in the `docs` folder. It will have also generated a Dash docset in the `docs/docsets` folder.

[constraid]: https://github.com/uptech/Constraid 
[jazzy]: https://github.com/realm/jazzy
[github]: https://github.com/cyphactor
[twitter]: https://twitter.com/cyphactor
