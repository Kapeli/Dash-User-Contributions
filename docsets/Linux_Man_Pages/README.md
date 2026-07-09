Linux Man Pages
=======================

Maintainers
-----------------------

**2026** scillidan

Build with modified [mandocset.py](https://github.com/scillidan/share_man-db/blob/main/scripts/mandocset.py). In zeal, you can use the feed URL:

- `http://zealusercontributions.vercel.app/api/docsets/Linux_Man_Pages.xml`
- Or `https://raw.githubusercontent.com/scillidan/share_man-db/refs/heads/main/Linux_Man_Pages.xml`

**2022** [Yanpas](https://github.com/Yanpas)  
- This docset (any man pages) may be generated using my python3 script (https://github.com/Yanpas/mandocset)
  - Script requires `man2html` utility (there is tgz archive in mandocset repo), it's available in any Debian derivative.
  - Currently it consists of posix and linux man pages. Posix man pages were taken from ubuntu's package [manpages-posix](https://launchpad.net/ubuntu/+source/manpages-posix). Linux man pages were taken from linux's [git](https://www.kernel.org/doc/man-pages/). Here is the [page](http://man7.org/linux/man-pages/dir_by_project.html) that has a list of popular linux man pages sources.
  - to run script : `python3 mandocset.py -o Linux -p resourse/man-pages-4.09/ resourse/man-pages-posix-2013-a/ -i etc/tux.png -I etc/tux@2x.png -f` e.g. Order of `p` args matters. Run script with `--help` arg for additional help.
- I wasn't able to find author of cgi converter utility. (it is very old) Beware of a bug: this cgi may go to endless loop with printf.1p file from posix and eat all your disk space.