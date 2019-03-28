from cpt.packager import ConanMultiPackager
import os

if __name__ == "__main__":
    print(os.environ)
    builder = ConanMultiPackager(options={"boost:python_version": "3.7"},
      env_vars={"Python_EXECUTABLE": os.environ['Python_EXECUTABLE'], "Python_INCLUDE_DIR": os.environ['Python_INCLUDE_DIR'], "Python_LIBRARY_RELEASE": os.environ['Python_LIBRARY_RELEASE']})
    builder.add_common_builds()
    builder.run()
