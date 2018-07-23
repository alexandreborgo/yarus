from setuptools import setup

requirements = [
    'mysql-connector-python',
    'flask',
    'yarus-common'
]

setup(
    name='yarus-engine',
    version='0.1',
    packages=['yarus', 'yarus.engine'],
    author='Alexandre Borgo',
    author_email='alexandre.borgo@free.fr',
    description='YARUS Engine',
    include_package_data=True,
    install_requires=requirements,
    classifiers=(
        'Programming Language :: Python :: 3.6',
    )
)
