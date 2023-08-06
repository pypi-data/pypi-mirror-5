filevault 
============

filevault is a class for managing a hash directory tree of files on a filesystem.

A Vault will:

* Create a hash directory tree of custom depth
* Spread out files to keep CLI snappy when traversing the tree
* Scale to hundreds of thousands of files
* Obfuscate directory paths and filenames

how to install
===================

Setuptools::

 easy_install filevault

Pip::

 pip install filevault

how to use
=================

How to create a default Vault object::
  
 from filevault import Vault

 v = Vault()

You may (and should) customize the Vault instance.  Here are the arguments:

vaultpath
 Where should the tree be created? Defaults to 'vault' in pwd.

depth
 How deep should the tree span? Defaults to 3 directories deep.

salt
 Add a custom salt for a unique and more secure tree, defaults to 'changeme'

Another custom example::
 
 from filevault import Vault

 v = Vault( vaultpath="/tmp/for-test", depth=2, salt="sugar" )

Now that we have a Vault object named v, we may review its two methods:

create_filename( seed, ext='', absolute=False )
 Create a valid vault filename seeded with input. Optional extension.
 Relative path from vaultpath by default unless absolute is True.

create_random_filename( ext='', absolute=False )
 Create a valid vault filename seeded with random input. Optional extension. 
 Relative path from vaultpath by default unless absolute is True.

Here is a full example::

 # import Vault class
 from filevault import Vault

 # create vault object named v, with custom path, depth, and salt
 v = Vault( vaultpath="/tmp/for-test", depth=2, salt="sugar" )

 # print a valid vault filename with extension
 print v.create_filename( "my-first-file", ".png" )

 # result:
 # 3/9/3993817d4f9b3867c6db29b23c9d2ff9bb8a87d89426002adbb6ed34289d9e32.png

 print v.create_filename( "my-first-file", ".png" )

 # Same result:
 # 3/9/3993817d4f9b3867c6db29b23c9d2ff9bb8a87d89426002adbb6ed34289d9e32.png

 # print a valid vault absolute filename with extension
 print v.create_filename( "my-first-file", ".png", absolute=True )

 # result:
 # /tmp/for-test/3/9/3993817d4f9b3867c6db29b23c9d2ff9bb8a87d89426002adbb6ed34289d9e32.png


 # print a random valid vault filename without extension
 v.create_random_filename()

 # result:
 # 6/1/6169d6ee0ac0bc63ab667fb94d9cc747df0c03596ac43e24a51b3517d74bdc42 


how may I thank you?
========================

Check out my `webpage to screenshot service <https://linkpeek.com>`_ and give me some feedback, tips, or advice.  Every little bit of help counts.


