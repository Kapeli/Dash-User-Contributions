package main

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"os"
	"strings"

	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/net/html"
)

func main() {

	db, err := initDB()
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	//
	// Add *ALL* the Methods
	//
	funcFiles := []string{
		"UVM/UVM.docset/Contents/Resources/Documents/index/Methods.html",
		"UVM/UVM.docset/Contents/Resources/Documents/index/Methods2.html",
		"UVM/UVM.docset/Contents/Resources/Documents/index/Methods3.html",
		"UVM/UVM.docset/Contents/Resources/Documents/index/Methods4.html",
		"UVM/UVM.docset/Contents/Resources/Documents/index/Methods5.html",
		"UVM/UVM.docset/Contents/Resources/Documents/index/Methods6.html",
		"UVM/UVM.docset/Contents/Resources/Documents/index/Methods7.html",
	}
	for _, f := range funcFiles {
		err = addGroup(db, f, "Method")
		if err != nil {
			log.Fatal(err)
		}
	}

	err = addGroup(db, "UVM/UVM.docset/Contents/Resources/Documents/index/Macros.html", "Macro")
	if err != nil {
		log.Fatal(err)
	}

	err = addGroup(db, "UVM/UVM.docset/Contents/Resources/Documents/index/Ports.html", "Interface")
	if err != nil {
		log.Fatal(err)
	}

	err = addGroup(db, "UVM/UVM.docset/Contents/Resources/Documents/index/Types.html", "Type")
	if err != nil {
		log.Fatal(err)
	}

	err = addGroup(db, "UVM/UVM.docset/Contents/Resources/Documents/index/Variables.html", "Variable")
	if err != nil {
		log.Fatal(err)
	}

	err = addGroup(db, "UVM/UVM.docset/Contents/Resources/Documents/index/Constants.html", "Constant")
	if err != nil {
		log.Fatal(err)
	}

	err = addGroup(db, "UVM/UVM.docset/Contents/Resources/Documents/index/Classes.html", "Class")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Done.")
}

func initDB() (*sql.DB, error) {
	os.Remove("uvm.docset/Contents/Resources/docSet.dsidx")
	db, err := sql.Open("sqlite3", "./UVM/UVM.docset/Contents/Resources/docSet.dsidx")
	if err != nil {
		return db, err
	}

	createClear := `
    CREATE TABLE if not exists searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);
    DELETE FROM searchIndex;
    CREATE UNIQUE INDEX if not exists anchor ON searchIndex (name, type, path);`

	_, err = db.Exec(createClear)
	if err != nil {
		return db, err
	}
	return db, nil
}

func addGroup(db *sql.DB, fileName, theType string) error {
	count := 0
	file, err := os.Open(fileName)
	if err != nil {
		log.Fatal(err)
	}

	// Find all classes
	tokenizer := html.NewTokenizer(file)

	inAThing := false
	proceed := true
	for proceed {
		tt := tokenizer.Next()
		switch tt {
		case html.ErrorToken:
			if tokenizer.Err() == io.EOF {
				proceed = false
				break
			}
			log.Fatalf("ERROR: '%s'\n", tokenizer.Err())
		case html.StartTagToken:
			t := tokenizer.Token()
			for _, a := range t.Attr {
				if t.Data == "td" && a.Key == "class" && a.Val == "IEntry" {
					inAThing = true
				}
				if a.Key == "href" {
					if inAThing {
						parts := strings.Split(a.Val, "#")
						if len(parts) < 2 {
							return fmt.Errorf("Parts was < 2: %s\n", strings.Join(parts, ","))
						}
						// fmt.Printf("%s method %s\n", strings.Join(parts[1:], "#"), a.Val)
						_, err := db.Exec(fmt.Sprintf("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('%s', '%s', '%s')", strings.Join(parts[1:], "#"), theType, "files/"+a.Val))
						if err != nil {
							return err
						}
						count++
					}
				}
			}
		case html.EndTagToken:
			t := tokenizer.Token()
			if t.Data == "td" { // End of a cell, reset inAThing
				inAThing = false
			}
		}
	}

	fmt.Printf("Entered %d %ss from %s\n", count, theType, fileName)
	return nil
}
