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
3. Run `jazzy` at the root of the repository, without any options

This will generate all the documentation in the `docs` folder. It will have also generated a Dash docset in the `docs/docsets` folder.

[constraid]: https://github.com/uptech/Constraid 
[jazzy]: https://github.com/realm/jazzy
[github]: https://github.com/cyphactor
[twitter]: https://twitter.com/cyphactor
