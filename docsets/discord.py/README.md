discord.py
=======================
[https://discordpy.readthedocs.io/en/stable/index.html](https://discordpy.readthedocs.io/en/stable/index.html)

Maintained by [UserBlackBox](https://github.com/UserBlackBox)

## Docset Generation
```bash
git clone https://github.com/Rapptz/discord.py
cd discord.py
cd docs
make html #build html docs
doc2dash -n discord.py -d . _build/html #convert to docset
python3 formatter.py #run formatter script to remove navbar and sidebar
```
* edit version in `meta.json`
* add icons to docset
* add guides to `docSet.dsidx`