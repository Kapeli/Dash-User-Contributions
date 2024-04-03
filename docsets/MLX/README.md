# MLX Docset

[MLX](https://github.com/ml-explore/mlx/) is an array framework for machine learning on Apple silicon, brought to you by Apple machine learning research.

## Author

- [Xavier Yang](https://github.com/ivaquero)

## Instructions

- Download the latest gh-pages files from https://github.com/ml-explore/mlx/tree/gh-pages
- Get an icon file (16×16) and rename it to `icon.png`, or just use the one in this repo
- Run the following commands

```cmd
cd mlx-gh-pages/docs
doc2dash -n MLX -i build/html/_static/mlx_logo.png -I build/html/index.html -f build/html
tar cvzf MLX.tgz MLX.docset
```
