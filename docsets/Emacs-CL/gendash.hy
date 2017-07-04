#!/usr/bin/env hy

(import [bs4 [BeautifulSoup NavigableString Tag]])
(import sys)
(import re)

(setv object-type-rx (re.compile "\s*(\w+):\s*"))

(defn print-sql [name type link]
  (print (.format "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('{0}', '{1}', '{2}');" name type link)))

(for [line (.readlines sys.stdin)]
  (setv fname (cut (.strip line) 2))
  (with [f (open fname "r")]
        (setv soup (BeautifulSoup f "html.parser"))
        (for [defun (.find_all soup "div" "defun")]
          (setv a-name (get (.find defun "a") "name"))
          (setv g (. defun strings))
          (setv obj-type (.group (.search object-type-rx (next g)) 1))
          (setv obj-name (next g))
          (print-sql obj-name
                     obj-type
                     (.format "{0}#{1}" fname a-name)))))
