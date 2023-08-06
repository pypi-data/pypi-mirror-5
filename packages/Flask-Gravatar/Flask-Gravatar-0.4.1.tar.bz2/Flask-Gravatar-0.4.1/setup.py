# coding: utf8

from setuptools import setup

setup(
        name='Flask-Gravatar',
        version='0.4.1',
        license='BSD',
        description='Small extension for Flask to make using Gravatar easy',
        long_description=open('README.rst').read(),
        author='Alexander Zelenyak aka ZZZ',
        author_email='zzz.sochi@gmail.com',
        url='https://github.com/zzzsochi/Flask-Gravatar/',
        platforms='any',

        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],

        install_requires=['Flask'],

        packages=['flaskext'],
        namespace_packages=['flaskext'],
)
