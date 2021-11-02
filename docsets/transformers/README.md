# Transformers Docset

[Transformers](https://github.com/huggingface/transformers) (formerly known as
`pytorch-transformers` and `pytorch-pretrained-bert`) by
[Hugging Face](https://huggingface.co) provides state-of-the-art general-purpose
 architectures for Natural Language Understanding (NLU) and Natural Language
 Generation (NLG). This repository contains the Dash docset of the
 documentation, and steps required to replicate it.

## Author

#### Venkat

- Github: [venkatasg](https://github.com/venkatasg)
- Twitter: [_venkatasg](https://twitter.com/_venkatasg)

(I am not related to the Hugging Face team or the `transformers` project in
anyway. I only created the Dash docset because I love the transformers library
and Dash)

## Prerequisites

Ensure that `pytorch`, `tensorflow` and `transformers` are installed in the
environment you are currently working in. If one of `tensorflow` or `pytorch`
isn't installed, then documentation will only be generated for the one you do
have installed.

## Building the Docset

`transformers` uses  the
[sphinx_rtd_theme](https://sphinx-rtd-theme.readthedocs.io/en/stable/).
Unfortunately, it isn't easy to hide the navigation sidebar like in some other
themes. To build the documentation for easy readability on Dash, follow these
steps.

1. Follow the instructions on the
[transformers repository](https://github.com/huggingface/transformers/tree/master/docs)
to generate the documentation **up until the build line** : `make html`.
2.  Before building, add the `hidesidebar.css` file to the
`docs/source/_static/css/` folder.
3. Open `docs/source/conf.py` and add the following line towards the end of the
file (in the function definition
`def setup(app)`): `app.add_stylesheet('css/hidesidebar.css')`. This will hide
the sidebar, remove unneccessary buttons and the Hugging Face logo.
4. Now build using `make html`. There will probably be a bunch of warnings -
search [issues](https://github.com/huggingface/transformers/issues) in the
transformers repository if the build fails.
5. Generate the Dash docset using [doc2dash](https://doc2dash.readthedocs.io/en/stable/).
This is the command I use(which needs to be run within the `docs/` folder, same
as where you built the documentation):

`doc2dash -i PATH_TO_ICON@2x.png -u https://huggingface.co/transformers/index.html# -n transformers -j -f -v -d DESTINATION_PATH_FOR_DOCSET_build/html/`.

6. Before archiving docset, go into the package contents of the `.docset` file
and add the following to the `plist` file. The FallbackURL would need to be
replaced with the one given below.

```
    <key>DashDocSetFallbackURL</key>
	<string>https://huggingface.co/transformers/</string>
    <key>DashDocSetKeyword</key>
	<string>transformers</string>
	<key>DashDocSetPluginKeyword</key>
	<string>transformers</string>
	<key>DashWebSearchKeyword</key>
	<string>transformers</string>
```

7. Now archive and submit [as instructed](https://github.com/Kapeli/Dash-User-Contributions)

## Minor issues

Depending on the size of your Dash window, a navigation bar might show up on
the top with a button (a hamburger button) to open the sidebar. Clicking on the
button will lead to an empty space on the left margin. Just click the button
again to get back your space. To get rid of the top bar, set your Dash window to
a wider width.
