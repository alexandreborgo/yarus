from setuptools import setup

requirements = [
    'mysql-connector-python',
    'requests',
    'yarus-common'
]

setup(
    name='yarus-tasks-manager',
    version='0.1',
    packages=['yarus', 'yarus.tasksmanager'],
    author='Alexandre Borgo',
    author_email='alexandre.borgo@free.fr',
    description='YARUS Tasks Manager',
    include_package_data=True,
    install_requires=requirements,
    classifiers=(
        'Programming Language :: Python :: 3.6',
    ),
    entry_points={
        'console_scripts': [
            'yarus-tasks-manager=yarus.tasksmanager.entry_point:tasksmanager_entry_point'
        ]
    }
)
