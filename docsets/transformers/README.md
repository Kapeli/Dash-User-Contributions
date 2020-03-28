# Transformers Docset

[Transformers](https://github.com/huggingface/transformers) (formerly known as `pytorch-transformers` and `pytorch-pretrained-bert`) by [Hugging Face](https://huggingface.co) provides state-of-the-art general-purpose architectures for Natural Language Understanding (NLU) and Natural Language Generation (NLG). This repository contains the Dash docset of the documentation, and steps required to replicate it.

## Author

#### Venkat

- Github: [venkatasg](https://github.com/venkatasg)
- Twitter: [_venkatasg](https://twitter.com/_venkatasg)

(I am not related to the Hugging Face team or the `transformers` project in anyway. I only created the Dash docset because I love the transformers library and Dash)

## Prerequisites

Ensure that `pytorch`, `tensorflow` and `transformers` are installed in the environment you are currently working in. If one of `tensorflow` or `pytorch` isn't installed, then documentation will only be generated for the one you do have installed.

## Building the Docset

`transformers` uses  the [sphinx_rtd_theme](https://sphinx-rtd-theme.readthedocs.io/en/stable/). Unfortunately, it isn't easy to hide the navigation sidebar like in some other themes. To build the documentation for easy readability on Dash, follow these steps.

1. Follow the instructions on the [transformers repository](https://github.com/huggingface/transformers/tree/master/docs) to generate the documentation **up until the build line*** : `make html`.
2.  Before building, add the `nosidebar.css` file to the `docs/source/_static/css/` folder.
3. Open `docs/source/conf.py` and add the following line towards the end of the file (in the function definition `def setup(app)`): `app.add_stylesheet('css/hidesidebar.css')`. This will hide the sidebar, remove unneccessary buttons and the Hugging Face logo.
4. Now build using `make build`. There will probably be a bunch of warnings - lookup issues on the [transformers repository](https://github.com/huggingface/transformers/issues) if the build fails.
5. Generate the Dash docset using [doc2dash](https://doc2dash.readthedocs.io/en/stable/). This is a minimal command that will automatically add it to Dash: `doc2dash -A -u https://huggingface.co/transformers/index.html# -n transformers -j -f _build/html/`. This needs to be run within the `docs/` folder, same as where you built it.

## Minor issues

Depending on the size of your Dash window, a navigation bar might show up on the top with a button (a hamburger button) to open the sidebar. Clicking on the button will lead to an empty space on the left margin. Just click the button again to get back your space. To get rid of the top bar, set your Dash window to a wider width. This may be more of an issue on the iOS app than on the Mac.