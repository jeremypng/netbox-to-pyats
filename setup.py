from setuptools import setup

setup(
    name='netbox-to-testbed',
    version='0.1',
    py_modules=['netbox_to_testbed'],
    install_requires=[
        'Click',
        'rich',
        'python-dotenv',
        'pynetbox',
        'pyyaml'
    ],
    entry_points='''
        [console_scripts]
        netbox-to-testbed=netbox_to_testbed:cli
    ''',
)
