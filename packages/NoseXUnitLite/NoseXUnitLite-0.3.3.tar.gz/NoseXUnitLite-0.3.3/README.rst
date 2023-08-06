
NoseXUnitLite - JUnit like XML reporting for Nose
=================================================

This is a stripped down version of NoseXUnit. We wanted to generate an XML output for nose, but the dependencies
of NoseXUnit were too much just for one XML file, so we choose to package a lighter version. 


What is missing here:
- code coverage
- pylint code analysis

If you want just an XML output for nose, you are a the right place!


Example use
-----------

    nosetests --with-nosexunitlite [options] [(optional) test files or directories]
    
You can specify (all optionals):

- The XML output folder with --core-target=PATH,
- The folder containing the Python sources with --source-folder=PATH, 

This is just a lighter repackaging of nosexunit: http://nosexunit.sourceforge.net
