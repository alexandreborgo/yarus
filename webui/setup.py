from setuptools import setup

requirements = [
    'requests',
    'pyyaml',
    'flask'
]

setup(
    name='yarus-webui',
    version='0.1',
    packages=['yarus', 'yarus.webui'],
    author='Alexandre Borgo',
    author_email='alexandre.borgo@free.fr',
    description='YARUS Web User Interface',
    install_requires=requirements,
    include_package_data=True,
    classifiers=(
        'Programming Language :: Python :: 3.6',
    )
)
