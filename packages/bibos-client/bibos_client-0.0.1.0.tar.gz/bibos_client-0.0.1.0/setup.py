from setuptools import setup

setup(
    name='bibos_client',
    version='0.0.1.0',
    description='Clients for the BibOS system',
    url='https://github.com/magenta-aps/',
    author='C. Agger and J.U.B. Kragh, Magenta ApS',
    author_email='carstena@magenta-aps.dk',
    license='GPLv3',
    packages=['bibos_client'],
    install_requires=['netifaces', 'bibos_utils'],
    scripts=['bin/register_in_bibos_admin'],
    zip_safe=False
)
