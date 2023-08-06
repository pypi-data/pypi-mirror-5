sh.test script test runner
==========================
`sh.test` is a test runner that can be used to write functional tests as single
executable scripts. `sh.test` will find and execute these tests and report on
the test status. In addition, `sh.test` is able to export the test results as
JUnit compatible XML, which makes it easy to integrate the test runs in your CI
server.

Installation
------------
You can install `sh.test` from pip

    pip install `sh.test`

If you want to install the latest version directory from the github repository,
checkout the repository and run:

    python setup.py install

After `sh.test` is installed, a single executable `sh.test` will be available in
your path. 

If you want to install `sh.test` in user space or you do not have root privileges
to install `sh.test` globally, append the `--user` option to the installation 
command. This will install `sh.test` in `$HOME/.local`. Note that you might have 
to put `$HOME/.local/bin` in your `PATH`.

Writing and running tests
-------------------------
You can see a few very limited examples in the `test_scripts` folder. `sh.test` 
searched for files that contain the word `test` in their name and that are 
executable. Those file are executed by `sh.test` and if they fail to execute 
(exit status != 0) the test is marked as failed. 

By default `sh.test` searches recursively in the current working directory, but
you can specify directories to search for script or test script as command line
options. For example:

    sh.test test_script

This will search for all test script in the `test_sript` folder and execute 
them.

Working directories and test data
---------------------------------
By default, `sh.test` will execute all test in the current working directory. 
You can use the `--cwd` option to tell sh.test to switch to the tests script 
parent folder before execution. This can be helpful if you want to store test
data next to your script.

In order to allow you to create temporary output during a test run, `sh.script`
creates and exposes a dedicated temporary folder for each test. The path to 
the folder is stored in the `TEST_DIR` environment variable and the folder
will be automatically removed after the test execution. Here is a simple
example of a test script that creates an output file and then `diffs` the file
against some expected output. The folder structure looks like this::

    test_script/
        test_use_dir.sh
        use_dir.sh

Here is the content of the test script `test_use_dir.sh`::

    #!/bin/bash

    echo "TEST" > $TEST_DIR/testfile
    diff -q use_dir.txt $TEST_DIR/testfile

The script writes its results to a file in `$TEST_DIR` and compares it against
a `use_dir.txt` file located next to the script. The test can be successfully 
executed with:

    sh.test --cwd test_script/test_use_dir.sh

Please note the `--cwd` option that is necessary to run the test as the test
depends on files located relative to the test script.
