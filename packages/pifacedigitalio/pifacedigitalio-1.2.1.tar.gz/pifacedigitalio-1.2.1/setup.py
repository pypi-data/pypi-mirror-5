import sys
import subprocess
from distutils.core import setup


PY3 = sys.version_info.major >= 3
PYTHON_CMD = "python3" if PY3 else "python"


# change this to True if you just want to install the module by itself
MODULE_ONLY = False

INSTALL_PIFACECOMMON_CMD = \
    "git clone https://github.com/piface/pifacecommon.git && " \
    "cd pifacecommon && " \
    "{} setup.py install".format(PYTHON_CMD)


class InstallFailed(Exception):
    pass


def run_cmd(cmd, error_msg):
    success = subprocess.call([cmd], shell=True)
    if success != 0:
        raise InstallFailed(error_msg)


def install_pifacecommon():
    print("Installing pifacecommon.")
    run_cmd(INSTALL_PIFACECOMMON_CMD, "Failed to install pifacecommon.")


def check_pifacecommon():
    try:
        import pifacecommon
        # TODO version numbers
    except ImportError:
        print("pifacecommon is not installed.")
        install_pifacecommon()


if "install" in sys.argv and not MODULE_ONLY:
    try:
        check_pifacecommon()
    except IOError as e:
        if (e[0] == errno.EPERM):
            sys.stderr.write("Install script must be run as root.")
            sys.exit(1)


setup(
    name='pifacedigitalio',
    version='1.2.1',
    description='The PiFace Digital I/O module.',
    author='Thomas Preston',
    author_email='thomasmarkpreston@gmail.com',
    url='https://github.com/piface/pifacedigitalio',
    py_modules=['pifacedigitalio'],
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
    keywords='piface digital raspberrypi openlx',
    license='GPLv3+',
    requires=[
        'pifacecommon',
    ]
)
