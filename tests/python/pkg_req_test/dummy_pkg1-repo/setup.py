from setuptools import setup

if __name__ == '__main__':
    setup(
        name='dummy_pkg1',
        version='1.0.0',
        install_requires=[
            'dummy_pkg2==1.0.0'
            # 'opencv-python == 4.5.1.48'
        ],
        entry_points={
            # the console_scripts entry point creates the xdoctest executable
            'console_scripts': [
                'dummy_pkg1 = dummy_pkg1.__main__:main'
            ]
        },
        packages=['dummy_pkg1'],
    )
