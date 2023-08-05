# min-pypi-hello

A minimalist example of PyPI packaging.
( 
[view on pypi](https://pypi.python.org/pypi/minpypihello/);
[view on GitHub](https://github.com/hupili/min-pypi-hello)
)

   * A module of called `minpypihello` that you can import and print a helloworld.
   * A script that can be executed directly to print a helloworld message.

## 1. Check the Project and Study Files

Run `./myhello` and see if it works as intended. 
Navigate under this repo and see those files for an example layout.

    min-pypi-hello/
    ├── MANIFEST.in
    ├── README.md
    ├── README.txt
    ├── minpypihello
    │   ├── __init__.py
    │   └── modhello.py
    ├── myhello
    └── setup.py

## 2. Package

Build source archive: `python setup.py sdist`.

Test:

   * Find your package in `dist/minpypihello-x.tar.gz`,
   where `x` is the version number.
   * Uncompress the archive and go to its root.
   * Install `python setup.py install`.
   You can add `--user` to install under your home.
   * Try `myhello` (not `./myhello`).
   If you `$PATH` is set properly and the install is successful, 
   you should see the printed hello message.
   * Try to import `minpypihello.modhello` from a Python script
   (see code of `myhello` for an example).

## 3. Distribute to PyPI

Register: Use `python setup.py register` and go through the procedure as prompt. 

Upload: `python setup.py upload`.

[more info.](http://docs.python.org/2/distutils/packageindex.html)

## Reference

   * distutils: 
   <http://docs.python.org/2/distutils/>
   * A list of package metadata: 
   <http://docs.python.org/2/distutils/setupscript.html#additional-meta-data>
