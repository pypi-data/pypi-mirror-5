from . import conf, shortcuts
import os
import subprocess
import sys


class BowerAdapter(object):
    """Adapter for working with bower"""

    def __init__(self, bower_path, components_root):
        self._bower_path = bower_path
        self._components_root = components_root

    def is_bower_exists(self):
        """Check is bower exists"""
        if shortcuts.is_executable(self._bower_path)\
                or shortcuts.which(self._bower_path):
            return True
        else:
            return False

    def create_components_root(self):
        """Create components root if need"""
        if not os.path.exists(self._components_root):
            os.mkdir(self._components_root)

    def install(self, packages):
        """Install package from bower"""
        proc = subprocess.Popen(
            [self._bower_path, 'install'] + list(packages),
            cwd=self._components_root,
        )
        proc.wait()

    def _get_package_name(self, line):
        """Get package name#version from line"""
        prepared_line = line.decode(
            sys.getfilesystemencoding(),
        )
        if '#' in prepared_line:
            for part in prepared_line.split(' '):
                if '#' in part and part:
                    return part[:-1]

        return False

    def freeze(self):
        """Yield packages with versions list"""
        proc = subprocess.Popen(
            [self._bower_path, 'list', '--offline', '--no-color'],
            cwd=conf.COMPONENTS_ROOT,
            stdout=subprocess.PIPE,
        )
        proc.wait()

        packages = filter(bool, map(
            self._get_package_name, proc.stdout.readlines(),
        ))

        return iter(set(packages))


bower_adapter = BowerAdapter(conf.BOWER_PATH, conf.COMPONENTS_ROOT)
