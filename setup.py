from setuptools import setup

desc = 'Define methods that can dynamically shift between synchronous and async'
long_desc = f'''{desc}

Please star the repo on `GitHub <https://github.com/ashafer01/python-ambisync>`_!
'''

setup(
    name='ambisync',
    version='0.2.0',
    author='Alex Shafer',
    author_email='ashafer@pm.me',
    url='https://github.com/ashafer01/python-ambisync',
    license='MIT',
    description=desc,
    long_description=long_desc,
    py_modules=['ambisync'],
)
