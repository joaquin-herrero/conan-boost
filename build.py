from cpt.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager(options={"boost:python_version": 3.7, "boost:python_executable": os.environ['Python_EXECUTABLE'], "boost:python_include_dir": os.environ['Python_INCLUDE_DIR'], "boost:python_lib_dir": os.environ['Python_LIBRARY_RELEASE']})
    builder.add_common_builds()
    builder.run()
