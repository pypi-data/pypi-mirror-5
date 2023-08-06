Exoline: Command Line for Exosite
=================================

Exoline is a set of commands for accessing the Exosite [One Platform](http://exosite.com/products/onep) from the command line.

- **exo** - command for the [RPC API](http://developers.exosite.com/display/OP/Remote+Procedure+Call+API)

- **exodata** - command for the [HTTP Data Interface API](http://developers.exosite.com/display/OP/HTTP+Data+Interface+API)


Installation 
------------

To install the latest released version of exoline:

```bash

    $ pip install --upgrade exoline
```

Alternatively, install straight from github:

```bash

    $ pip install -e git://github.com/dweaver/exoline#egg=exoline
```


Environment Variables
---------------------

For convenience, several command line options may be replaced by environment variables.

* EXO\_HOST: host, e.g. m2.exosite.com. This supplies --host to exo and --url for exodata.


Help 
----

For help, run each command with -h from the command line.


Test
----

To run the tests, install the packages in test/requirements.txt, and then type:

```bash

    $ cd test
    $ ./test.sh
```

Examples
--------

Here are some examples of common tasks with Exoline.

* Upload a Lua script

```bash

    $ exo script translate_gps.lua e469e336ff9c8ed9176bc05ed7fa40d?????????     
    Updated script RID: 6c130838e14903f7e12d39b5e76c8e3?????????
```

* Monitor output of a script

```bash

    $ exo read e469e336ff9c8ed9176bc05ed7fa40d????????? translate_gps.lua --follow 
    2013-07-09 11:57:45,line 2: Running translate_gps.lua...
    2013-07-09 12:00:17,"line 12: New 4458.755987,N,09317.538945,W
    line 23: Writing 4458.755987_-09317.538945"
    2013-07-09 12:15:41,"line 12: New 4458.755987,N,09317.538945,W
    line 23: Writing 4458.755987_-09317.538945"
```

* Write raw data

```bash

    $ exo write e469e336ff9c8ed9176bc05ed7fa40d????????? gps-raw --value=4458.755987,N,09317.538945,W
```


TODO
----

- fix install issue with pyonep 0.5
- add sparklines output
- add support for /provision/register to get vendor info from CIK
- add support in read for multiple rids
- Make the info command take multiple rids (or stdin)
- Make the script command take multiple rids (or stdin)
- Add --watch flag to script upload so script loads automatically
- Support binary datasource format
- find out why aliases is sometimes a list, sometimes a dict
- make tests run faster by combining resource create commands into one
