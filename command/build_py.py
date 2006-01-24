
from distutils.command.build_py import build_py as old_build_py

class build_py(old_build_py):

    def find_package_modules(self, package, package_dir):
        modules = old_build_py.find_package_modules(self, package, package_dir)

        # Find build_src generated *.py files.
        build_src = self.get_finalized_command('build_src')
        modules += build_src.py_modules_dict.get(package,[])

        return modules

    def find_modules(self):
        old_py_modules = self.py_modules[:]
        new_py_modules = filter(lambda i:type(i) is type(str), self.py_modules)
        self.py_modules[:] = new_py_modules
        modules = old_build_py.find_modules(self)
        self.py_modules[:] = old_py_modules
        return modules

    # XXX: Fix find_source_files for item in py_modules such that item is 3-tuple
    # and item[2] is source file.
