from setuptools import setup

setup(
    name='weebify',
    version='0.0.1',
    py_modules=['weebify'],
    install_requires=['enzyme>=0.4.1'],

    entry_points = {
        'console_scripts': [
            'weebify = weebify:main'
        ]
    },

    url='https://github.com/TronPaul/weebify',
    license='MIT',
    author='Mark McGuire',
    author_email='mark.b.mcg@gmail.com',
    description='A script to modify mkvs for anime enthusiasts'
)
