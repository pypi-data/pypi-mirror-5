from setuptools import setup, find_packages
setup(
    name='docutils_html5_writer',
    version='0.1.0',
    author='James H. Fisher, Kozea',
    license='public domain',
    install_requires=['docutils', 'html5lib'],
    packages=find_packages(),
)
