CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);
CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);
CREATE TABLE temp(name TEXT, type TEXT, path TEXT);
.mode csv temp
.import data.csv temp
DELETE FROM temp WHERE name in ("numeric literals", "string literals", "keywords");
INSERT INTO temp (name, type, path) VALUES ("count", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("cycle", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("repeat", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("accumulate", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("chain", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("compress", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("drop-while", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("remove", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("group-by", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("islice", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("map", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("take-while", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("tee", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("zip-longest", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("product", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("permutations", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("combinations", "Function", "language/core.html#included-itertools");
INSERT INTO temp (name, type, path) VALUES ("multicombinations", "Function", "language/core.html#included-itertools");
INSERT INTO searchIndex(name, type, path) SELECT * FROM temp;
DROP TABLE temp;
