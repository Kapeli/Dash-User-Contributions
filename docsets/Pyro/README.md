# Pyro Docset

## Author

- Songpeng Zu (https://github.com/beyondpie)
- Xavier Yang (https://github.com/ivaquero)

## Instructions

- clone https://github.com/pyro-ppl/pyro
- `cd pyro/docs`
- Modify `source/conf.py`, comment the `intersphinx_mapping` block
- run the following command

```cmd
make html
doc2dash -n Pyro -i source/_static/img/pyro_logo.png -f -I index.html -v build/html && tar cvzf Pyro.tgz Pyro.docset
```
