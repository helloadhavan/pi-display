from setuptools import setup, find_packages

setup(
    name='pidisplay',
    version='0.1.0',
    description='a display status server for Raspberry Pi',
    packages=find_packages(),
    install_requires=[
        'adafruit-circuitpython-ssd1306',
        'adafruit-circuitpython-busdevice',
        'flask',
        'RPi.GPIO',
        'Pillow',  # PIL (Python Imaging Library)
        'smbus2'   # For I2C communication (smbus)
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
