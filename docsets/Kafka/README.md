Kafka
=======================
Author: Guillaume Balaine ([@Igosuki][3])
#### Generation Steps:
* Clone the docset [repo][4]
* Make sure you have [go][1] installed then inside the cloned repository
run `go get` 
* Run `go run src/generate.go` (it's a single main package script)

Additionally you can provide a --version flag which currently defaults to 0.8.2

#### Known Bugs:
* None, submit any you find [here][2]

#### Planned Improvements:
* Detect new versions from Apache's documentation automatically
* Better flag defaults to manage truncation sqlite and page downloading

[1]: https://golang.org/
[2]: https://github.com/Igosuki/kafka_docset/issues
[3]: https://twitter.com/igosuki
[4]: https://github.com/Igosuki/kafka_docset
