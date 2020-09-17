Six Docset
=======================

## Author

[Filippo Valsorda](https://filippo.io). [FiloSottile](https://github.com/FiloSottile). [@FiloSottile](https://twitter.com/FiloSottile).

## Creation

```
httrack "http://pythonhosted.org/six/" -O "pythonhosted" "+*pythonhosted.org/six/*" -v
doc2dash -v -n Six pythonhosted/pythonhosted.org/six/
```

Set `dashIndexFilePath` to `index.html`.
