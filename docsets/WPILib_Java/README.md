WPILib Java
=======================

Hello! My name is Calum McConnell <calumlikesapplepie@gmail.com>, or @TheMageKing
on Github.  I am a member of FRC Team 999, and I wanted to be able to access the
WPI documentation while we were at competitions easily.  We use Java on my team, but
I decided to generate both documentation sets.  I am aware that WPILib bundles the
documentation with their code as best as they can, however, its nice to be able to
pull out ones phone and just look at the docs there.

I generated this documentation on a linux system, following various instructions online
for the most part.  Clone the allwpilib repo onto your local machine, and run their
javadoc task (./gradlew javadoc).  That concludes step 1.

Step 2 requires that you either use a Mac to generate the docset using
Kapeli's javadocset program or to use william8th's program of the same name on
any other machine.  William's program is basically the same as Kapeli's, but
reimplemented in Golang for portability.  To run it, install go, then use
`go get go get github.com/william8th/javadocset` to get williams program.
You may need to do some PATH finagling to get the created binary into your path:
it wound up in `$HOME/go/bin` for me.

Run `javadocset WPILib_Java $REPO/allwpilib/docs/build/docs/javadoc`.  It will create
a docset folder in your working directory, and populate it propperly.  When I did this,
I got a barrage of warnings about how it couldnt find an entity for some items: perhaps
I will try fix that in a future update of this docset.

I will try to keep this up-to-date, but I can't promise that I will remeber in a few years.  
As such, if you see it is out of date, please follow these instructions (and those on the
dash-user-contributions repo) to update it.

I may write a script to updates at some point (probably later in the 2020 season), but
for now, I am just doing this manually.
