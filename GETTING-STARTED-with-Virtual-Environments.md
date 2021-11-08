# Working with Notebook's terminal

Complete guide: from https://docs.python.org/3/tutorial/venv.html

In a new terminal interface be sure to work inside your default user home directory, by default it should be "/home/jovyan".
Everything saved outside of this directory will be lost.

## How to create a new virtual environment
Python applications will often use packages and modules that don’t come as part of the standard library. Applications will sometimes need a specific version of a library, because the application may require that a particular bug has been fixed or the application may be written using an obsolete version of the library’s interface.

This means it may not be possible for one Python installation to meet the requirements of every application. If application A needs version 1.0 of a particular module but application B needs version 2.0, then the requirements are in conflict and installing either version 1.0 or 2.0 will leave one application unable to run.

The solution for this problem is to create a virtual environment, a self-contained directory tree that contains a Python installation for a particular version of Python, plus a number of additional packages.

Different applications can then use different virtual environments. To resolve the earlier example of conflicting requirements, application A can have its own virtual environment with version 1.0 installed while application B has another virtual environment with version 2.0. If application B requires a library be upgraded to version 3.0, this will not affect application A’s environment.

The module used to create and manage virtual environments is called venv. venv will usually install the most recent version of Python that you have available. If you have multiple versions of Python on your system, you can select a specific Python version by running python3 or whichever version you want.

To create a virtual environment, decide upon a directory where you want to place it, and run the venv module as a script with the directory path:

```
python -m venv tutorial-env
```

This will create the tutorial-env directory if it doesn’t exist, and also create directories inside it containing a copy of the Python interpreter and various supporting files.

A common directory location for a virtual environment is .venv. This name keeps the directory typically hidden in your shell and thus out of the way while giving it a name that explains why the directory exists. It also prevents clashing with .env environment variable definition files that some tooling supports.

Once you’ve created a virtual environment, you may activate it.

On Unix or MacOS, run:

```
source tutorial-env/bin/activate
```





## How to install additional python libraries

You can install, upgrade, and remove packages using a program called pip. By default pip will install packages from the Python Package Index, <https://pypi.org>.
You can browse the Python Package Index by going to it in your web browser.

You can install the latest version of a package by specifying a package’s name:
```
(tutorial-env) $ python -m pip install novas
```

You can also install a specific version of a package by giving the package name followed by == and the version number:
```
(tutorial-env) $ python -m pip install requests==2.6.0
```


pip uninstall followed by one or more package names will remove the packages from the virtual environment.



pip show will display information about a particular package:
```
(tutorial-env) $ pip show requests
```

pip list will display all of the packages installed in the virtual environment:
```
(tutorial-env) $ pip list
novas (3.1.1.3)
numpy (1.9.2)
pip (7.0.3)
requests (2.7.0)
setuptools (16.0)
```


The requirements.txt can then be committed to version control and shipped as part of an application. Users can then install all the necessary packages with install -r:

```
(tutorial-env) $ python -m pip install -r requirements.txt
```



## How to manage also non-python libraries with Conda
From: https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html

Update conda to the current version. Type the following:
```
conda update conda
```

Conda allows you to create separate environments containing files, packages, and their dependencies that will not interact with other environments.
If you want to proceed with conda environments follow these steps:

1. Create a new environment and install a package in it.

We will name the environment snowflakes and install the package BioPython. At the Anaconda Prompt or in your terminal window, type the following:
```
conda create --name snowflakes biopython
```

Conda checks to see what additional packages ("dependencies") BioPython will need, and asks if you want to proceed:
```
Proceed ([y]/n)? y
```
Type "y" and press Enter to proceed.

2. To use, or "activate" the new environment, type the following:
```
    Windows: conda activate snowflakes

    macOS and Linux: conda activate snowflakes
```

3. To see a list of all your environments, type:
```
conda info --envs
```
A list of environments appears, similar to the following:
```
conda environments:

    base           /home/username/Anaconda3
    snowflakes   * /home/username/Anaconda3/envs/snowflakes
```

4. Change your current environment back to the default (base): 
```
conda activate
```

### Managing packages with conda
Install 
Check to see if a package you have not installed named "beautifulsoup4" is available from the Anaconda repository:
```
conda search beautifulsoup4
```

Conda displays a list of all packages with that name on the Anaconda repository, so we know it is available.

Install this package into the current environment:
```
conda install beautifulsoup4
```
Check to see if the newly installed program is in this environment:
```
conda list
```







## How to create a kernel to use within the notebook

From 
https://ipython.readthedocs.io/en/stable/overview.html
and
https://ipython.readthedocs.io/en/stable/install/kernel_install.html

One of Python’s most useful features is its interactive interpreter. It allows for very fast testing of ideas without the overhead of creating test files as is typical in most programming languages. However, the interpreter supplied with the standard Python distribution is somewhat limited for extended interactive use.

If you want to have multiple IPython kernels for different virtualenvs or conda environments, you will need to specify unique names for the kernelspecs.

By default ipykernel is installed in your environment. 

In the following example we will install Tensorflow in a virtual environment and create a kernel from it.

First step is to create a virtual environment called tensorflow inside your user home directory (/home/jovyan):

```
python -m venv tensorflow
```

This will create a new directory called tensorflow.

Then we must activate the virtual environment:
```
source tensorflow/bin/activate
```

Now it's possible to install ipykernel, tensorflow (and other desired libraries) in the activated virtual environment :
```
python -m pip install ipykernel
python -m pip install tensorflow
```

Last step is to create a new kernel named Tensorflow with ipykernel from our environment
```
python -m ipykernel install --user --name tensorflow --display-name "Python (Tensorflow)"
```

It's also possible to initialize a notebook using this kernel within the virtual environment:
```
jupyter lab
```

The new kernel will be available from the Launcher and from the drop-down menu in the notebook. 
