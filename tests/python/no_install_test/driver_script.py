"""
This is the driver script and also is the place where this test is documented.

The following demonstrates how scripts that rely on modules with a proper
Python structure, but are not installed can be invoked.

We will test:

    * Using a driver script that lives parallel to the package
    * Using a main script (`__main__.py`) that lives inside the package

CommandLine:

    ########
    # Test 1 - Call a driver script in the package's parent directory.
    ########

    # This works because we are in the same directory as the package It is
    # implicitly in our python path

    cd ~/misc/tests/python/no_install_test
    python -m not_installed_package

    ########
    # Test 2 - Call a driver script outside the package's parent directory.
    ########
    # This also works.

    cd ~/misc/tests/python
    python ~/misc/tests/python/no_install_test/driver_script.py

    ########
    # Test 3 - Call the main script via its full path in the package parent directory
    ########
    # Strange, this doesn't work. I thought it would. It errors with
    # `ImportError: attempted relative import with no known parent package`

    cd ~/misc/tests/python/no_install_test
    python ~/misc/tests/python/no_install_test/not_installed_package

    # This also fails with the following variations

    cd ~/misc/tests/python/no_install_test
    python not_installed_package

    cd ~/misc/tests/python/no_install_test
    python not_installed_package/__main__.py

    ########
    # Test 4 - Call the main script via its module name in the package parent directory
    ########
    # This works.

    cd ~/misc/tests/python/no_install_test
    python -m not_installed_package
"""


import not_installed_package
from not_installed_package.__main__ import main


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/no_install_test/driver_script.py
    """
    not_installed_package.foo()
    main()
