# pagegroup
made this thing to not waste ink &amp; paper printing my LEGALLY retrieved manga

## convert a directory of pages to a directory of groupped pages

```sh
$ ./pagegroup --verbose ./pages ./groupped-pages
```

## pdftool: convert pdfs to a directory of pages

```sh
$ ./pdftool toimgs 1240 1754 file.pdf ./pages
```

## pdftool: convert a directory of pages to a pdf

```sh
$ ./pdftool fromimgs ./groupped-pages ./file-groupped.pdf
```
