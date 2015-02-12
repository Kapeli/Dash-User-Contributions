Android Gradle Plug-in DSL Reference
====================================

Created by [Tarek Belkahia](https://github.com/tokou)

## Generation

Steps to generate the docset:
* Download the plugin command reference package from the [Android Plug-in for Gradle page](https://developer.android.com/tools/building/plugin-for-gradle.html) ([direct link](https://developer.android.com/shareables/sdk-tools/android-gradle-plugin-dsl.zip)).
* Clone the script from [android-gradle-plugin-dash-docset](https://github.com/tokou/android-gradle-plugin-dash-docset)
* Run it giving the zip file as first argument (Tested on Mac OS X, requires ruby and sqlite3 gem)

```
./android-gradle-plugin-dash-docset.rb android-gradle-plugin-dsl.zip
```
