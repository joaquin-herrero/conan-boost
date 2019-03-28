from conans import ConanFile, tools

import os
import tarfile

class BoostConan(ConanFile):
    name = "boost"
    version = "1.69"
    license = "MIT License"
    author = "Joaquín Herrero Herrero"
    url = "https://github.com/joaquin-herrero/conan-boost"
    description = "Boost library"
    topics = ("boost", "c++")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC":[True, False], "python_version": [3.5, 3.7]}
    default_options = "shared=False", "fPIC=True", "python_version=3.5" 
    generators = "cmake"
    url_package = "https://dl.bintray.com/boostorg/release/1.69.0/source/boost_1_69_0"
    boost_root = "boost_1_69_0"
    skip_python = False

    def win_sources(self):
        zip_extension = ".zip"
        file = self.boost_root + zip_extension

        tools.download(self.url_package + zip_extension, file)

        print("-Unpacking file: %s..." % file)
        tools.unzip(file)

        print("-Removing file: %s..." % file)
        os.unlink(file)

    def unix_sources(self):
        tar_extension = ".tar.gz"
        file = self.boost_root + tar_extension
        
        tools.download(self.url_package + tar_extension, file)

        print("-Unpacking file: %s..." % file)
        tar = tarfile.open(file, "r:gz")
        tar.extractall()
        tar.close()

        print("-Removing file: %s..." % file)
        os.unlink(file)

    def set_python(self):
        python_include_dir = self.env.get("Python_INCLUDE_DIR", "None")
        python_library = self.env.get("Python_LIBRARY_RELEASE", "None")
        python_executable = self.env.get("Python_EXECUTABLE", "None")

        # Skip python configuration if variables are not set
        if python_include_dir == "None" or python_library == "None" or python_executable == "None":
            print( "-Skipping python configuration...")
            self.skip_python = True
            return

        new_config_file_name = "project-config.jam.new"
        new_config_file = open(new_config_file_name, 'w+')
        
        old_config_file_name = "project-config.jam"
        with open(old_config_file_name, 'r') as old_config_file:
            for line in old_config_file:
                if line.lstrip().startswith("using python"):
                    new_config_file.write("    using python : %s : %s : %s : %s ; %s" % (self.options.python_version, python_executable, python_include_dir, python_library, os.linesep))
                else:
                    new_config_file.write(line)

        new_config_file.close()

        os.unlink(old_config_file_name)
        os.rename(new_config_file_name, old_config_file_name)

    def build_type(self):
        if self.settings.build_type == "Release" or self.settings.build_type == "RelWithDebInfo":
            return "variant=release"
        else:
            return "variant=debug"

    def linkage(self):
        if self.options.shared == True:
            return "shared"

        return "static"

    def flags(self):
        flags = ""
        c_flags = ""
        cxx_flags = ""

        if self.settings.os != "Windows":
            if self.options.fPIC == True:
                c_flags += "-fPIC "
                cxx_flags += "-fPIC "

        cxx_version = self.env.get("CXX_STANDARD", 14)
        if self.settings.compiler == "Visual Studio":
            cxx_flags += "/std:c++%s " % cxx_version
        else:
            cxx_flags += "-std=c++%s " % cxx_version

        c_flags += self.env.get("C_FLAGS", "")
        cxx_flags += self.env.get("CXX_FLAGS", "")


        c_flags = "" if c_flags == "" else 'cflags="%s"' % c_flags
        cxx_flags = "" if cxx_flags == "" else 'cxxflags="%s"' % cxx_flags
        flags = c_flags + ' ' + cxx_flags

        if self.skip_python == True:
            flags += "--without-python"

        print(flags)
        return flags;

    def platform(self):
        if self.settings.arch == "x86_64":
            return "address-model=64"
        elif selg.settings.arch == "x86":
            return "address-model=32"
        else:
            raise Exception("Binary does not exist for these platform")

    def build(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
        
        print("-Downloading sources...")

        if self.settings.os == "Windows":
            self.win_sources()
        else:
            self.unix_sources()

        # cd into ./boost_1_69_0
        os.chdir(self.boost_root)
        
        print("-Configuring sources...")
        
        command = "bootstrap.bat" if self.settings.os == "Windows" else "./bootstrap.sh"
        self.run(command)

        self.set_python()

        print("-Building...")

        exe = "b2.exe" if self.settings.os == "Windows" else "./b2"
        command = "%s %s %s --hash stage link=%s runtime-link=shared -j %s %s" % (exe, self.platform(), self.flags(), self.linkage(), tools.cpu_count(), self.build_type())

        print(command)
        self.run(command)
        
    def package(self):
        boost_dir = "%s/%s" % (self.build_folder, self.boost_root)

        self.copy("*.h", dst="include/boost", src="%s/boost" % boost_dir )
        self.copy("*.hpp", dst="include/boost", src="%s/boost" % boost_dir )
        self.copy("*.ipp", dst="include/boost", src="%s/boost" % boost_dir )
        self.copy("*.lib", dst="lib", src="%s/stage" % boost_dir, keep_path=False)
        self.copy("*.dll", dst="bin", src="%s/stage" % boost_dir, keep_path=False)
        self.copy("*.so*", dst="lib", src="%s/stage" % boost_dir, keep_path=False)
        self.copy("*.dylib", dst="lib", src="%s/stage" % boost_dir, keep_path=False)
        self.copy("*.a", dst="lib", src="%s/stage" % boost_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.libs += ["util", "dl", "pthread"]

        if self.options.shared == True:
            self.cpp_info.defines = ["BOOST_ALL_NO_LIB"]
