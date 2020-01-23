Installation
============

```
git clone <...>
cd cpp-utils
mkdir -p build/Release # use "Debug" if you want to build in debug
cd build/Release
cmake ../..
make
sudo make install
sudo ldconfig
```

Uninstall
=========

```
cd build/Release
sudo make uninstall
```

Additional Information
======================

In order to setup the project, edit the file CMakefile.txt in the root fo the project. Then fills in the macros as you wish up until you arrive in the "DO NOT EDIT PART". All the definitions are commented so you should be able to fill it easily.

The cmake has the following capabilities:

 - you add *.cpp files either inside `src/main/cpp` or `src/test/cpp` or in a subdirectory of them.
 - you add *.hpp files either inside `src/main/include` or `src/test/include` or in a subdirectory of them.
 - `src/main` compiles the main artifact, either a EXE, a static or dynamic library. `src/test` compiles an executable you can call containing all the unit tests.
 - you are required top call cmake from one of 2 directories: `build/Debug` or `build/Release`: use the former to implicitly compile in debug or the second if you plan to make the optimzed version of your artifact (e.g., `cmake ../..` in  `build/Debug` directory).
 - Whenever you add a new file, be sure to call `cmake ../..` to update the script.
