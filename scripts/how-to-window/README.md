
### How to install, setup and make package

Download Anaconda and install it

https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Windows-x86_64.exe

Download GnuWin32 CoreUtils and add the location of the bin folder to the WINDOW PATH.

https://gnuwin32.sourceforge.net/packages/coreutils.htm

Download git and add the folder of cmd and bin into the WINDOW PATH.

Download 7-Zip and add it to the WINDOW PATH.

Create conda environment to work on.
```
conda create -n myenv python=3.11.15 -y
```

Activate your conda environment

```
conda activate myenv
```

And then install the common packages by running the following
```
pip install -r scripts/requirements/requirements.txt
```

To make the package run this command
```
make package
```