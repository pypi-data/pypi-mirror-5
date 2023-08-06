from distutils.core import setup

setup(
    name='diffscuss',
    version='1.0.1',
    author='Edmund Jorgensen',
    author_email='edmund@hut8labs.com',
    packages=['diffscuss', 'diffscuss.support',
              'diffscuss.mailbox'],
    scripts=['bin/diffscuss'],
    url='http://github.com/hut8labs/diffscuss/',
    license='LICENSE.txt',
    description='Plain-text code review format.',
    install_requires=[
        "PyGithub==1.14.2",
        "argparse==1.2.1",
        "requests==1.2.0"
    ],
)
