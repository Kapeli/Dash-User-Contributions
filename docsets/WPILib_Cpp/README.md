WPILib Cpp
=======================

Hello! My name is Calum McConnell <calumlikesapplepie@gmail.com>, or @TheMageKing
on Github.  I am a member of FRC Team 999, and I wanted to be able to access the
WPI documentation while we were at competitions easily.  We use Java on my team, but
I decided to generate both documentation sets.  I am aware that WPILib bundles the
documentation with their code as best as they can, however, its nice to be able to
pull out ones phone and just look at the docs there.

I generated this documentation on a linux system, following various instructions online
for the most part.  Clone the allwpilib repo onto your local machine, and the edit
the docs/build.gradle file so that, within the 'doxygen' task, it has the following:

```language:gradle
    generate_html true
    generate_docset true
    disable_index true
    search_engine false
    generate_treeview false

```

(the generate_html line should already be there)
Then, go to the root of the allwpilib repo and run ./gradlew doxygen
Now, go to docs/build/docs/doxygen/html, and run make.  This will create a file that
hosts the docset (note the default name is org.doxygen.Project.docset).  Now, make
**will** claim that the build failed: this is because, unless you are on a mac, you
lack xcode.  However, it still succeeded: toss the folder it created into a tarball
and call it a day.

I will try to keep this up-to-date, but I can't promise that I will remeber in a few years.  
As such, if you see it is out of date, please follow these instructions (and those on the
dash-user-contributions repo) to update it.

I may write a script to updates at some point (probably later in the 2020 season), but
for now, I am just doing this manually.
