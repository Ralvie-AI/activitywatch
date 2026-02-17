# hooks/hook-shapely.py
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = []

for src, _ in collect_dynamic_libs("shapely"):
    name = src.split("/")[-1]

    if name.startswith("libgeos"):
        binaries.append((src, "Frameworks"))
