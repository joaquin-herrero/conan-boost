import os

from conans import ConanFile, CMake, tools


class BoostTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package"
        cmake.definitions["Python_LIBRARY_RELEASE"] = self.env.get("Python_LIBRARY_RELEASE", "")
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')

    def test(self):
        if not tools.cross_building(self.settings):
            os.chdir("bin")
            if self.settings.os == "Linux":
                self.run("export LD_LIBRARY_PATH=$(pwd) && .%sexample" % os.sep)
            else:
                self.run(".%sexample" % os.sep)