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


Coding style Convention
=======================

The code should follow these conventions:

 - In type hierarchy, alsways define the `this` and every parent type,as follows:
    ```
    class Foo: public Bar {
    public:
        using This = Foo;
        using Super1 = Bar;
    }
    ```
    In this way, if we need to add a new template, you simply need to update the using declaration, not everything in the code. If you have multiple parent classes, append to the Super name an index;

 - pure virtual classes should be name `IXXX` (e.g., `IFoo`);

 - virtual classes which has at least one concrete field should be named `AbstractXXX` (e.g., `AbstractFoo`);

 - each important class is specified in a single file;

 - each enumeration class is specific in its file;

 - enumeration should inherit from `AbstractEnum`;

 - templates should resides in `.hpp` files, not in `.tpp` ones;

 - files should be named with the name of the important class, or the name of the enumeration, or with a `camelCase` convention;

 - utility functions can resides in their own file: if this is the case, group the utilities per functionality and call the files with the plural name of such functionality. For instance, if the functionality is "validating paths", call the file `pathValidators.hpp`;

 - Always declare the move/copy assignemnt/constructors, virtual destructor and a constructor: You can make them default, but always defined them;

 - A custom implementation of move assigment/constructor should call `std::move` on every sub field;

 - Class names shoud follow `PascalCase`;

 - enumerations should follow `snake_case`, with at the end a `_e` (e.g., `my_enum_e`);

 - use `auto` as much as possible;

 - always prefer `++a` over `a++` to avoid worthless copy assignment calls;

 - in template variadic, use always constant references to avoid invalid desturctor calls:

    ```
    template <typename ...OTHER>
    void foo(const OTHER&... others);
    ```
