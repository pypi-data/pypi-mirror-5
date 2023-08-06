from setuptools import setup, find_packages
import os


setup(
    author="Ben Lopatin",
    author_email="ben.lopatin@wellfireinteractive.com",
    name='django-organizations',
    version='0.1.7',
    description='Group accounts for Django',
    long_description=open(os.path.join(os.path.dirname(__file__),
        'README.rst')).read(),
    url='https://github.com/wellfire/django-organizations/',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires=[
        'Django>=1.4',
        'django-extensions>=0.9',
    ],
    #test_suite='tests.runtests.runtests',
    include_package_data=True,
    packages=find_packages(exclude=["tests.tests", "tests.test_app", "tests"]),
    zip_safe=False
)
