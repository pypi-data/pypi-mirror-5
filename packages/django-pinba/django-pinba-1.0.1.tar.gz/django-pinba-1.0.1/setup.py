from setuptools import setup, find_packages


setup(
    name='django-pinba',
    version="1.0.1",
    description='django pinba',
    keywords="django pinba",
    long_description=open('README.rst').read(),
    author="GoTLiuM InSPiRiT",
    author_email='gotlium@gmail.com',
    url='http://github.com/gotlium/django-pinba',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    install_requires=[
        'iscool_e.pynba>=0.3.5',
        'django'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
