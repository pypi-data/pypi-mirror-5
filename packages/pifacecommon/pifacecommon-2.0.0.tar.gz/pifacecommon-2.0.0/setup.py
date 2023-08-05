import sys
import errno
import subprocess
from distutils.core import setup


# change this to True if you just want to install the module by itself
MODULE_ONLY = False

SCRIPT_ROOT = "https://raw.github.com/piface/pifacecommon/master/bin/"
UNBLACKLIST_SPI_CMD = \
    "curl {}unblacklist-spi-bcm2708.sh | bash".format(SCRIPT_ROOT)
SETUP_SPI_CMD = "curl {}spidev-setup.sh | bash".format(SCRIPT_ROOT)
SETUP_GPIO_CMD = "curl {}gpio-setup.sh | bash".format(SCRIPT_ROOT)


class InstallFailed(Exception):
    pass


def run_cmd(cmd, error_msg):
    success = subprocess.call([cmd], shell=True)
    if success != 0:
        raise InstallFailed(error_msg)


def unblacklist_spi_bcm2708():
    run_cmd(UNBLACKLIST_SPI_CMD, "Could not unblacklist spi_bcm2708.")


def setup_spi():
    unblacklist_spi_bcm2708()
    run_cmd(SETUP_SPI_CMD, "Could not set up SPI.")


def setup_gpio():
    run_cmd(SETUP_GPIO_CMD, "Could not set up GPIO.")


if "install" in sys.argv and not MODULE_ONLY:
    setup_spi()
    setup_gpio()


setup(
    name='pifacecommon',
    version='2.0.0',
    description='The PiFace common functions module.',
    author='Thomas Preston',
    author_email='thomasmarkpreston@gmail.com',
    license='GPLv3+',
    url='https://github.com/piface/pifacecommon',
    packages=['pifacecommon'],
    long_description=open('README.md').read() + open('CHANGELOG').read(),
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 or "
        "later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='piface raspberrypi openlx',
)
