from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="gfwlist2privoxy",
    version="1.0.2",
    license='MIT',
    description="convert gfwlist to privoxy action file",
    author='snachx',
    author_email='snachx@gmail.com',
    url='https://github.com/snachx/gfwlist2privoxy',
    packages=['gfwlist2privoxy', 'gfwlist2privoxy.resources'],
    package_data={
        'gfwlist2privoxy': ['README.rst', 'LICENSE', 'resources/*']
    },
    install_requires=[],
    entry_points="""
    [console_scripts]
    gfwlist2privoxy = gfwlist2privoxy.main:main
    """,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    long_description=long_description,
)
