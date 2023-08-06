from distutils.core import setup

setup(
    name='debacl',
    version='0.2.0',
    author='Brian P. Kent',
    author_email='bpkent@gmail.com',
    packages=['debacl', 'debacl.test'],
    scripts=['bin/gauss_demo.py'],
    url='https://github.com/CoAxLab/DeBaCl',
    license='LICENSE.txt',
    description='Density-Based Clustering',
    long_description=open('README.txt').read(),
    install_requires=[
        "python-igraph == 0.6.5",
        "numpy >= 1.7.0",
        "scipy >= 0.11.0",
	"matplotlib >= 1.2.0"
    ],
)
