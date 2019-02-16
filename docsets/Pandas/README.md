# Pandas

This docset was created by  [Philipp Keller](https://github.com/philippkeller)

## How to build this docset

- Check out Pandas
    ```
    git clone https://github.com/pandas-dev/pandas
    cd pandas
    git tag -l # check for latest version
    git checkout tags/v0.24.1 # replace 0.24.1 with latest version
    ```
- To build the docs of Pandas you need to first have anaconda, then do:
    ```
    conda env create -f environment.yml
    conda activate pandas-dev # on my machine I also needed to do conda init zsh
    source activate pandas-dev
    python setup.py build_ext --inplace -j 4
    python make.py html --num-jobs 4
    ```
- To convert it into docset:
    ```
    cd build
    # Removes previous compilation if it exists
    #  [[ -e rm -rf ~/Library/Application\ Support/doc2dash/DocSets/Pandas.docset ]] && rm
       -r ~/Library/Application\ Support/doc2dash/DocSets/Pandas.docset   
    doc2dash -A -n Pandas -I html/index.html html
    ```
- Archive docset (as a preparation for the git push):
    ```
    cd ~/Library/Application\ Support/doc2dash/DocSets
    tar --exclude='.DS_Store' -cvzf /tmp/pandas.tgz Pandas.docset
    ```
- Fork/clone the source Kapeli repo, update the `docset.json` file with new author/version/etc, and update this README.md file as necessary.
- Replace `pandas.tgz.txt` with /tmp/pandas.tgz.
- Download Pandas icons:
    ```
    wget https://s3.eu-central-1.amazonaws.com/hansaplast-share/pandas/pandas_logo-16.png -O icon.png
    wget https://s3.eu-central-1.amazonaws.com/hansaplast-share/pandas/pandas_logo-32.png -O icon@2x.png
    ```
- Commit and push to your forked repo.
- Issue a pull request.


