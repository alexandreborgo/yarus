from setuptools import setup

requirements = [
    'mysql-connector-python',
    'pyyaml'
]

setup(
    name='yarus-common',
    version='0.1',
    packages=['yarus', 'yarus.common'],
    author='Alexandre Borgo',
    author_email='alexandre.borgo@free.fr',
    description='YARUS Common',
    include_package_data=True,
    install_requires=requirements,
    classifiers=(
        'Programming Language :: Python :: 3.6',
    )
)
