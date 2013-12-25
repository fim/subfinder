Sub finder tool for OpenSubtitles API
====================

This is a simple app to search & fetch sub files from OpenSubtitles

Installation
------------

```sh
$ pip install https://github.com/fim/subfinder/tarball/master
```

Usage
-----

- Automatically get the best subs for a movie

```sh
$ subfinder /path/to/movie.avi
```

- Check & download english subs for a movie

```sh
$ subfinder -i /path/to/movie.avi
```

- Fetch all available subs for a specific language (language code must be in
        ISO 639-2)

```sh
$ subfinder -l ell -a /path/to/movie.avi
```

- Fetch subtitles for multiple files:

```sh
$ subfinder -l ell /path/to/series/season1/*.mkv
```
