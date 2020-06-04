WPILib Java Dash Docset
=======================

[WPILib](http://wp.wpi.edu/wpilib/) is the library used in the [FIRST Robotics Competition](http://www.firstinspires.org/robotics/frc) to program robots.

Docs generally update once a year in January with every new competition season, with minor updates through April or May as the season progresses.

Docset Author&ensp;·&ensp;[Calum McConnell](https://github.com/TheMageKing)

## Generate the Docset

  1. Use git to get a local copy of the [allwpilib repository](https://github.com/wpilibsuite/allwpilib.git).  I recommend you use a shallow clone for speed and space reasons, eg: `git clone --depth 1 github.com/wpilibsuite/allwpilib.git`.
  2. In your repository, run `./gradlew generateJavaDocs` to instruct gradle to create the javadocs.  Gradle will place them in
  `docs/build/docs/javadoc/`.  This will be your target for when you run javadocset.
  3. Use [javadocset](https://github.com/Kapeli/javadocset) to generate the Dash docset, using the docs you found in step 2.
  Note, however, that Kapeli's program will **not** run on computers that are not Mac's with Xcode.  Use william8th's [go implementation](https://github.com/william8th/javadocset) instead.

Additionally, the javadocs can be found posted officially online [here](http://first.wpi.edu/FRC/roborio/release/docs/java/)
