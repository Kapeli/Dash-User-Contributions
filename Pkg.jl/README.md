`Pkg.jl`
=======================

* Who am I: [singularitti](https://github.com/singularitti)
* Complete instructions on how to generate the docset, including:
  * Install Julia and [dashing](https://github.com/technosophos/dashing)
  
  * Fork the [original repo](https://github.com/JuliaLang/Pkg.jl)
  
  * Change the CSS file `docs/src/assets/custom.css` from
  
    ```css
    #documenter .docs-sidebar .docs-logo > img {
        max-height: 12em;
    }
    ```
  
    to
  
    ```css
    .docs-sidebar {
      display: none !important;
    }
    
    .docs-main header.docs-navbar .docs-right {
      display: none !important;
    }
    
    .docs-main {
      width: 100%;
      max-width: none !important;
      margin-left: 0 !important;
      padding-left: 1rem !important;
      padding-right: 1rem !important;
    }
    ```
  
  * Build the documentation using Julia
  
  * Run
  
    ```bash
    cd docs/build
    dashing create
    ```
  
  * Edit the `docs/build/dashing.json` to
  
    ```json
    {
        "name": "Pkg.jl",
        "package": "Pkg.jl",
        "index": "index.html",
        "selectors": {
            "h2": "Section",
            "h1": {
                "type": "Guide",
                "regexp": "\\d+\\.\\s+(.*)",
                "replacement": "$1"
            },
            ".docstring header": [
                {
                    "type": "Function",
                    "requiretext": "Function",
                    "matchpath": "api.html"
                },
                {
                    "type": "Type",
                    "requiretext": "Type"
                },
                {
                    "type": "Command",
                    "requiretext": "REPL command"
                }
            ]
        },
        "icon32x32": "assets/logo.png",
        "allowJS": false,
        "ExternalURL": "https://pkgdocs.julialang.org/v1.6/"
    }
    ```
  
  * Run `dashing build`
  
    