from setuptools import setup, find_packages

setup(
    name='pidisplay',
    version='0.0.0',
    description='a display status server for Raspberry Pi',
    packages=find_packages(),
    install_requires=[
        'adafruit-circuitpython-ssd1306',
        'adafruit-circuitpython-busdevice',
        'flask'
    ],
)
