# runtime hook: run ก่อน import shapely
import os
import sys

if sys.platform == "darwin":
    exe_dir = os.path.dirname(sys.executable)
    frameworks = os.path.abspath(
        os.path.join(exe_dir, "..", "Frameworks")
    )

    # ให้ dyld มองเห็น libgeos
    os.environ["DYLD_LIBRARY_PATH"] = frameworks + ":" + \
        os.environ.get("DYLD_LIBRARY_PATH", "")
