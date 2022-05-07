from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="gfwlist2privoxy",
    version="2.0.0",
    license='MIT',
    description="convert gfwlist to privoxy action file",
    author='snachx',
    author_email='snachx@gmail.com',
    url='https://github.com/snachx/gfwlist2privoxy',
    packages=['gfwlist2privoxy', 'gfwlist2privoxy.resources'],
    package_data={
        'gfwlist2privoxy': ['README.rst', 'LICENSE', 'resources/*']
    },
    python_requires=">=3.6",
    install_requires=[],
    entry_points="""
    [console_scripts]
    gfwlist2privoxy = gfwlist2privoxy.main:main
    """,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    long_description=long_description,
)
