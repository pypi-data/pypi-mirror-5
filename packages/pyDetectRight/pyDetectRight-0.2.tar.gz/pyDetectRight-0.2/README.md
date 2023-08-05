pyDetectRight
=============

A Python wrapper for DetectRight Java API. 
This wrapper is based on Py4J to communicate with Java library officially provided. 
For native Java API, please visit http://detectright.com/


Install
-------------

Dependency:  `py4j`  --  http://py4j.sourceforge.net/

Download `pyDetectRight` from https://github.com/caesar0301/pyDetectRight and run

        python setup.py install


How to use
-------------

You can use `pyDetectRight` in your program like below:


        from pyDetectRight import DetectRight
        from py4j.protocol import Py4JJavaError

        db = "path/to/detectright.data"

        # detect user agent string
        dr = DetectRight(db)
        dr.start_server()
        devmap = dr.getProfileFromUA("Android 4.1")
        print devmap

        # detect user agent profile
        uaprofile = "http://nds1.nds.nokia.com/uaprof/N6303iclassicr100.xml"
        print dr.getProfileFromUAProfile(uaprofile)


        # detectright.jar in the library folder is under evalution.
        # some functions are disabled and exception will be raised.
        # try:
        # 	handler.getAllDevices()
        # except Py4JJavaError as e:
        # 	print e

        # do not forget to stop the server to release resources
        dr.stop_server()


Note:

Before using this library, you need to download the detectright database from official website.
This database is about 100MB. 

The `detectright.jar` file published along with this library is an evalution version, so some methods may be
out of function when you use it. If you have the complete version, you can replace it under "java/lib" 
folder in your project.

Happy coding ;)
