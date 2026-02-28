"""
Copyright (c) Facebook, Inc. and its affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

__version__ = "0.0.1"
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent

# Long description from README.md:
def load_readme():
    with open(REPO_ROOT / "README.md", encoding="utf8") as f:
        readme = f.read()
    return readme


class CMakeExtension(Extension):
    def __init__(self, name):
        Extension.__init__(self, name, sources=[])


def get_cmake():
    return "cmake3" if shutil.which("cmake3") is not None else "cmake"


def has_windows_compiler():
    return any(shutil.which(c) is not None for c in ("cl", "clang-cl", "g++"))


class CMakeBuild(build_ext):
    configured = False

    def run(self):
        try:
            out = subprocess.check_output([get_cmake(), "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: "
                + ", ".join(e.name for e in self.extensions)
            )

        cmake_version = re.search(r"version\s*([\d.]+)", out.decode().lower()).group(1)
        cmake_version = [int(i) for i in cmake_version.split(".")]
        if cmake_version < [3, 17]:
            raise RuntimeError("CMake >= 3.17 is required to build gtn")
        if os.name == "nt" and not has_windows_compiler():
            raise RuntimeError(
                "A C/C++ compiler was not found. Install Visual Studio Build Tools "
                "with the Desktop development with C++ workload, then reopen the shell."
            )

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        srcdir = str(REPO_ROOT)
        # required for auto - detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + extdir,
            "-DPYTHON_EXECUTABLE=" + sys.executable,
            "-DPROJECT_SOURCE_DIR=" + srcdir,
            "-DGTN_BUILD_PYTHON_BINDINGS=ON",
            "-DGTN_BUILD_EXAMPLES=OFF",
            "-DGTN_BUILD_BENCHMARKS=OFF",
            "-DGTN_BUILD_TESTS=OFF",
        ]
        if shutil.which("ninja") is not None:
            cmake_args += ["-G", "Ninja"]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]
        cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg]
        build_args += ["--parallel", str(os.cpu_count() or 4)]

        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get("CXXFLAGS", ""), self.distribution.get_version()
        )
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        cmake = get_cmake()
        if not CMakeBuild.configured:
            subprocess.check_call(
                [cmake, srcdir] + cmake_args, cwd=self.build_temp, env=env
            )
            CMakeBuild.configured = True
        subprocess.check_call([cmake, "--build", "."] + build_args, cwd=self.build_temp)


setup(
    name="gtn",
    version=__version__,
    author="GTN Contributors",
    description="Automatic differentiation with WFSTs",
    url="https://github.com/gtn-org/gtn",
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    packages=["gtn", "gtn.criterion"],
    package_dir={"": "."},
    ext_modules=[
        CMakeExtension("gtn.graph"),
        CMakeExtension("gtn.device"),
        CMakeExtension("gtn.autograd"),
        CMakeExtension("gtn.cuda"),
        CMakeExtension("gtn.utils"),
        CMakeExtension("gtn.rand"),
        CMakeExtension("gtn.creations"),
        CMakeExtension("gtn.criterion.criterion"),
        CMakeExtension("gtn.functions"),
        CMakeExtension("gtn.parallel"),
    ],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    license="MIT licensed, as found in the LICENSE file",
    python_requires=">=3.5",
)
