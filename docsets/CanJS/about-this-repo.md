# How to Build a Contrib. Repo. for CanJS

## Initial Setup

* Fork and clone the [Kapeli Contribution Repository ](https://github.com/kapeli/Dash-User-Contributions)
	* 	You'd then issue some command like `git clone https://github.com/<github-username>/Dash-User-Contributions`
* Clone the [CanJS.com Repository](https://github.com/bitovi/canjs.com)
	* 	ex. `git clone https://github.com/bitovi/canjs.com`
* Clone the [CanJS Repository](https://github.com/bitovi/canjs)

**NOTE**: remember to initialize any submodules for the repositories, or run `nom`, etc after cloning. Check each repo. for more instructions on how to set things up.

	
## Generate the Docset Archives for each Major.Minor version of CanJS (except the latest one)

We skip the latest `Major`.`Minor` version because new patches on the latest version will conflict with how Dash handles archived versions. We update the latest version later in the process.

* Change the branch of your CanJS repo to each Major.Minor version (e.g. 2.0, 1.1, ...). **Make sure to use the last patch version for each legacy version of CanJS**
* in the CanJS.com repo, move the `can` subdirectory to `can.submodule`
* now, symlink from your canjs repo into this canjs.com repo, using the name `can`. This allows you to control the version of the docs being built.
* Once that is set up, run `grunt docjs`
* Once grunt completes, compress the corresponding CanJS.docset directory with `tar --exclude='.DS-Store' -cvzf CanJS.tgz CanJS.docset` in that version's directory (e.g., 2.0, 1.1, ...)

Once you have properly compressed that version of CanJS, move on to the next by switching the branch in the canjs repo, and re-running `grunt docjs`

**NOTE**: if building docs for 1.1.x of CanJS, use the 1.1-legacy branch, and remove the comments from `.jshintrc`

## Now, Set up Dash-User-Contributions

[Read here](https://github.com/kapeli/Dash-User-Contributions)

Also, if you're seeing this, you're looking at a working repository for Dash-User-Contributions!

In Summary:

* Copy `Sample_Docsets` into the `docsets` directory
* Rename `Sample_Docsets` to `CanJS`
* In this new directory...
	* move `canjs-logo-16x16.png` from the canjs.com repo. over the `icon.png` file
	* move `canjs-logo-32x32.png` from the canjs.com repo. over the `icon@2x.png` file
* Copy each version above into its own directory, and place into the `versions` subdirectory
* Update README.md with appropriate instructions (see the current README.md for guidance)
* Update `docset.json` to reference all the versioned archives.
	* Refer to <https://github.com/Kapeli/Dash-User-Contributions/wiki/Docset-Versioning-Guidelines> for more guidance
	* Refer to <https://github.com/Kapeli/Dash-User-Contributions/issues/54>

## And Add the latest CanJS to Dash-User-Contributions

* Change the branch in the canjs repo. to the latest tagged version.
* Re-run `grunt docjs` to generate docs for that version, then compress it like above.
* In your new Dash-User-Contributions repo., remove Sample_Docset.tgz and replace with the newly created CanJS.tgz 
* Update the docset.json file to reference this version. Again refer to <https://github.com/Kapeli/Dash-User-Contributions/wiki/Docset-Versioning-Guidelines> for help with the version string format

Now you are ready to submit a pull request! Remember to do this AFTER the latest version of CanJS is tagged.

Pull requests should be submitted to : <https://github.com/Kapeli/Dash-User-Contributions/pulls>