CodeIgniter 3 Docset
=======================

## CodeIgniter
> CodeIgniter is an Application Development Framework - a toolkit - for people who build web sites using PHP. Its goal is to enable you to develop projects much faster than you could if you were writing code from scratch, by providing a rich set of libraries for commonly needed tasks, as well as a simple interface and logical structure to access these libraries. CodeIgniter lets you creatively focus on your project by minimizing the amount of code needed for a given task.

## Author

Note: I'm not the author of the CodeIgniter 3 documentation, I just generated the CodeIgniter 3 docset.

#### Rafael Schwemmer

- Twitter: [@textandbytes](https://twitter.com/textandbytes)
- GitHub: [Schwemmer](https://github.com/schwemmer)
- Web: <http://www.textandbytes.com/en>

## Building the Docset

- I used a modified version of Alexander Blunck's [Dash-Docset-Creator](https://github.com/alexblunck/Dash-Docset-Creator)
- Downloaded [CodeIgniter, Version 3.0.0](https://github.com/bcit-ci/CodeIgniter/archive/3.0.0.zip)
- Created 3 directories: `files_go_here`, `icon_goes_in_here`and `output` as required by the PHP script
- Copied the contents of the `user_guide` folder from CodeIgniter to the `files_go_here`directory
- Downloaded the CodeIgniter logo and saved it as `icon.png` under the `icon_goes_in_here` folder
- Added JavaScript support to the docset by adding this line to the `create-info.php` script:

  ```php
  $xml_string .= '<key>isJavaScriptEnabled</key><true/>';
  ```
- Modified the `create-docset.php` script to use a shell command to recursively copy the HTML files instead of non-recursively copying them by looping over the files:
  
  ```php
  shell_exec('cp -r files_go_here/ output/' . $config['docset_filename'] . '/Contents/Resources/Documents/');
  ```
- Removed the command that creates a `docs` sub-folder under `Contents/Resources/Documents`
- Instead of creating the TOC (Table of Contents) dynamically by looping over the HTML files non-recursively with the included `create-tokens.php` script which did not work for the CodeIgniter documentation, I created another directory called `TOC_goes_here`, downloaded the old Codeigniter 2.2 docset from the [Docset Direct Download Links](https://kapeli.com/docset_links) and copied its `Tokens.xml` file to the `TOC_goes_here`directory as `TOC.xml`, then modified the `create-docset.php` script to copy the file to the generated docset like so:

  ```php
  copy('TOC_goes_here/TOC.xml', 'output/'.$config['docset_filename'].'/Contents/Resources/Tokens.xml');
  ```
- Testing the generated docset showed that the old CodeIgniter 2.2 table of contents still works in CodeIgniter 3!

## Notes
The generated docset supports both searching from Dash as well as searching from within the documentation itself as you would on the CodeIgniter website. It also supports the old and the new style of browsing topics (old: topics on the left, new: topics on the top as a collapsible table of contents). Switching from new to old style can be toggled using the "Hamburger" icon on the top right.

## Bugs & Enhancements

If you have problems with this documentation set, or you would like to suggest
improvements, feel free to contact me.
