from . import conf
import subprocess
import sys
import os


def bower_install(packages):
    """Install package from bower"""
    proc = subprocess.Popen(
        ['bower', 'install'] + list(packages),
        cwd=conf.COMPONENTS_ROOT,
    )
    proc.wait()


def bower_freeze():
    """Yield packages with versions list"""
    proc = subprocess.Popen(
        ['bower', 'list', '--offline', '--no-color'],
        cwd=conf.COMPONENTS_ROOT,
        stdout=subprocess.PIPE,
    )
    proc.wait()

    yielded = []

    for line in proc.stdout.readlines():
        prepared_line = line.decode(
            sys.getfilesystemencoding(),
        )
        if '#' in prepared_line:
            for part in prepared_line.split(' '):
                if '#' in part and part not in yielded:
                    yield part
                    yielded.append(part)
                    break


def create_components_root():
    """Create components root if need"""
    if not os.path.exists(conf.COMPONENTS_ROOT):
        os.mkdir(conf.COMPONENTS_ROOT)
