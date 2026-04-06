tags:Math
date:2024-07-04
# Bertini

My first year at UWEC, I was given a great opportunity for student research.  A professor, the main developer of [Bertini](https://github.com/bertiniteam/b2), a mathematical package providing numerical homotopy continuation for solving systems of polynomial equations, needed help making Bertini easier to install and use by researchers in the field.

The professor had been writing Python bindings for the primarily C++ software for years and wanted help making it more easily installable. Because it was C++, we chose to target Conda, as it's a pretty standard tool for software packages. Conda allowed us to install all of Bertini's dependencies, which proved super helpful.

As we started our quest to make it installable with Conda, we realized we needed to port Bertini from using Autotools to the modern CMake as its build system. In the end, you can now install Bertini2 much more streamlined using Pip and CMake instead of cobbling together all the dependencies from different sources and compiling it with Autotools. 

[Here](https://github.com/ThisIsNotANamepng/b2) is my fork of the repo where I did my work.

This story is presented much more nicely in a PDF I presented at [CERCA](https://www.uwec.edu/orsp/students/cerca/) [Here](/static/BertiniPoster.pdf). 
