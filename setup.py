from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='rmen_app',
    version='0.1',
    description='RMEN app',
    # license="MIT",
    long_description=long_description,
    author='Mikhail Gareev',
    # author_email='foomail@foo.example',
    # url="http://www.foopackage.example/",
    packages=['rmen'],  #same as name
    # install_requires=['wheel', 'bar', 'greek'], #external packages as dependencies
    scripts=[
        'app/app.py']
)