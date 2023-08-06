from setuptools import setup

setup(
    name='ipython_doctester',
    author='Catherine Devlin',
    author_email='catherine.devlin@gmail.com',
    version='0.3.0',
    url='http://pypi.python.org/pypi/ipython_doctester/',
    py_modules = [
        "ipython_doctester",
        ],
    license='MIT',
    description='Run doctests in individual IPython Notebook cells',
    long_description=open('README.txt').read(),
    install_requires=[
        "ipython >= 1.0",
        "pyzmq >= 2.1.4",
        "requests",
        ]
)
