from cpt.packager import ConanMultiPackager
import os

if __name__ == "__main__":
    builder = ConanMultiPackager(options={"boost:python_version": "3.7"})
    builder.add_common_builds()
    builder.run()
