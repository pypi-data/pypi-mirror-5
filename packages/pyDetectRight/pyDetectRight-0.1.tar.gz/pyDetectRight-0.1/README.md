pyDetectRight
=============

A Python wrapper for DetectRight Java API. 
This wrapper is based on Py4J to communicate with Java library officially provided. 
For native Java API, please visit http://detectright.com/


Install
-------------

Dependency:  `py4j`  --  http://py4j.sourceforge.net/

Download `pyDetectRight` from https://github.com/caesar0301/pyDetectRight and 
run `python setup.py install`


How to use
-------------


First, run `./run_java_server.sh` to start py4j gateway for java;

Second, use pyDetectRight to process detection. See examples in folder "examples"


Note:

Before using this library, you need to download the detectright database from official website.
This database is about 100MB. 

The `detectright.jar` file published along with this library is an evalution version, so some methods may be
out of function when you use it. If you have the complete version, you can replace it under "java/lib" 
folder in your project.

Happy coding ;)
