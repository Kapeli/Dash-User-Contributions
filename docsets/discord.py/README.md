discord.py
=======================
[https://discordpy.readthedocs.io/en/latest/index.html](https://discordpy.readthedocs.io/en/latest/index.html)

Maintained by [UserBlackBox](https://github.com/UserBlackBox)

## Docset Generation
```bash
git clone https://github.com/Rapptz/discord.py
cd discord.py
cd docs
make html #build html docs
doc2dash -n discord.py -d . _build/html #convert to docset
./html-formatter.sh #run formatter script to remove navbar and sidebar
```
* edit version
* add icons
* add guides to SQLite db
