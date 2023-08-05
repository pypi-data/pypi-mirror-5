Introduction to reststore 
*************************

Why reststore?

 reststore is used by me and my friends as a simple way to share and store
 samples of malware.  Large volumes of files are what we're in it for.  We have
 demonstrated just about every possible way one can destroy a filesystem.  One
 day I'll write a guide on how things go bad when trying to store millions of
 files... 
 
What is reststore:

 * A convenient way to store large quantities of data.
 * Ability to access data locally or access it via a server hosting the
   reststore webapp. 
 * Chain together multiple webapp servers until they reach the single
   authoritative reststore webapp.

What's in reststore: 

 * A Python dictionary type Files or FilesClient object for seamless access
   of data via the configured hashing algorithm.
 * A set of command line operations to get put and list data.
 * A RESTful webapi so data can be accessed in a client agnostic manner. 



Project hosting provided by `github.com`_.


Install
=======

Simply run the following::

    > python setup.py install
    
or `PyPi`_:: 

    > pip install reststore
    

Getting started
===============


Coding with reststore
---------------------
Files and FilesClient are the two main classes used to access data from a store.

A local session:: 

 $ ipython

 In [1]: import reststore

 In [2]: files = reststore.Files()

 In [3]: files.
 files.get        files.hash_len   files.put        
 files.hash_func  files.index      files.select     

 In [3]: files.put("test data")
 Out[3]: 'eb733a00c0c9d336e65691a37ab54293'

 In [4]: files.put("test with some more data")
 Out[4]: 'a99fb3880c8ac126b3cf6163aa965305'

 In [5]: files.put("test with some more data... and more")
 Out[5]: 'e93a9d514c57f96d158864754f1ca330'

 In [6]: files['e93a9d514c57f96d158864754f1ca330']
 Out[6]: u'/tmp/files/00195/00065/3'

 In [7]: files.select(2,-1)
 Out[7]: ['e93a9d514c57f96d158864754f1ca330']

 In [8]: files.select(1,-1)
 Out[8]: [a99fb3880c8ac126b3cf6163aa965305', e93a9d514c57f96d158864754f1ca330']

 In [9]: for hexdigest in files:
    ...:     print hexdigest 
    ...:     
 eb733a00c0c9d336e65691a37ab54293
 a99fb3880c8ac126b3cf6163aa965305
 e93a9d514c57f96d158864754f1ca330

The exact same code above will work using the FilesClient class which will
seamlessly interface with a reststore webapp server.


Configuring reststore
---------------------

reststore has a very simple configuration system.  Configuration is applied
in the following order:

 * defaults from reststore.config
 * /etc/reststore.yaml
 * ~/reststore.yaml
 * environ <- each config value is written RESTSTORE_[INTERFACE]_[NAME]=Value

Example of the default config::

 $ cat ~/.reststore.yaml 
 
 client: {uri: 'http://127.0.0.1:8586/'}
 files: {assert_data_ok: false, hash_function: md5, name: files, root: /tmp, tune_size: 100000000}
 webapp: {debug: false, host: 127.0.0.1, port: 8586, proxy_requests: false, quiet: false,
 server: wsgiref}
     

Command line interface
----------------------

Exploring the command line interface should expose the core features of
reststore::

 $ reststorei -h

 NAME reststore - control over the reststore 

 SYNOPSIS
     reststore [COMMAND]

 Commands:
     
     get [OPTIONS FILE-OPTIONS] [HEXDIGEST] > stdout
         Attempt to retrieve a file and write it out to stdout.  A check is
         made in the local reststore first, if the file is in available, an
         attempt to read the file from the web reststore is made. 
     
         arguments 
             HASH define the hash to read from the reststore.

         options
             --weboff
                 This flag forces access to a local repository only.
             --uri=http://127.0.0.1:8586/
                 The uri to the reststore web server.

     put [OPTIONS FILE-OPTIONS] FILEPATH(s) 
         Put a file into the reststore.   
     
         arguments 
             A path to the file to load into the reststore.

         options
             --weboff
                 This flag forces access to a local repository only.
             --uri=http://127.0.0.1:8586/
                 The uri to the reststore web server.

     list [OPTIONS FILE-OPTIONS]
         list out hexdigests found in the reststore.   
     
         options
             --from=0
             --to=-1
             --weboff
                 This flag forces access to a local repository only.
             --uri=http://127.0.0.1:8586/
                 The uri to the reststore web server.

     len [OPTIONS FILE-OPTIONS]
         print out the number of files stored in the reststore.   
     
         options
             --weboff
                 This flag forces access to a local repository only.
             --uri=http://127.0.0.1:8586/
                 The uri to the reststore web server.

     web [OPTIONS FILE-OPTIONS] [[HOST:][PORT]] 
         Run the RESTful web app.
         
         arguments 
             HOST:PORT defaults to 127.0.0.1:8586

         options
             --server=wsgiref
                 Choose the server adapter to use.
             --debug=False 
                 Run in debug mode.
             --quiet=False
                 Run in quite mode.
             --proxy_requests=False
                 If True, this web app will proxy requests through to 
                 the authoritative server defined by the client uri.
             --uri=http://127.0.0.1:8586/
                 This client uri points to the authoritative (or next level
                 up) reststore web app.

 File options:
    --name=files
        Set the default reststore name (i.e. domain or realm) 
    --hash_function=md5
        Set the hash function to be used
    --tune_size=100000000
        Set the approximate size the reststore may grow up to.
    --root=/tmp
        Set the root for the reststore.
    --assert_data_ok=False
        Do extra checks when reading and writing data.



Issues
======

Source code for *reststore* is hosted on `GitHub
<https://github.com/provoke-vagueness/reststore>`_. 
Please file `bug reports <https://github.com/provoke-vagueness/reststore/issues>`_
with GitHub's issues system.


Change log
==========


version 0.0.0 (06/05/2013)





.. _github.com: https://github.com/provoke-vagueness/reststore
.. _PyPi: http://pypi.python.org/pypi/reststore
