Faker Docset
=============

##### Fzaninotto's Faker docset

 
# Author
I'm Adnan RIHAN, a Web and System developper, mainly for fun but also for work.

You can contact me by email (on my [Github page](https://github.com/Max13)) or on [Twitter](https://twitter.com/_Max13).

And finally, you can checkout my GPG keys on [Keybase](https://keybase.io/Max13)

# Prerequisites
- `dashing-0.4.1` (available on my homebrew tap `max13/dashing`)
- `wget`

# Generate the docset
This docset have been generated almost by hand

First I download the PHP docset `fzaninotto/faker`, which I copy to the corresponding Dash-User-Contributions directory. Then I download the `readme.md` HTML file from github with all dependencies (by hand for now)

Finally, my version of dashing allows to use the update command which will append the HTML files and index to the existing Faker docset.

# Known issues
None for now. But if you need anything, open an issue on my own repo: `https://github.com/Max13/dash-carbon` (Don't mind the name)
