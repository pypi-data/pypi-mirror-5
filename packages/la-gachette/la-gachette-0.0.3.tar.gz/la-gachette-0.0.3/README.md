gachette
========

[![Build Status](https://travis-ci.org/ops-hero/gachette.png?branch=master)](https://travis-ci.org/ops-hero/gachette)

Python module to setup working copy of specific branch for a project, launch build of packages via `trebuchet` and attach the packages to a specific stack, ready for deployment. This can be used from the CLI or programatically as a python library.
This will trigger the process on remote build machines, by using `fabric`.

Installation
============

This is actually in pypi, so you can do:

    $ pip install la-gachette

Or to install the latest version from github:

    $ git clone git@github.com:ops-hero/gachette.git
    $ cd gachette
    $ sudo pip install -e install
    $ gachette -l

The build machine needs to have installed `trebuchet`:

    $ ssh hero@192.168.1.5
    $ sudo pip install le-trebuchet

Concept
=======

`Stack` is an artefact that represents a list of packages in a specific version. It is versioned as well. It ensures
consistency of the version dependencies. Deployments are only based on `stack`; a specific stack is deployed, therefore
only the specified version of the packages are then installed. 

For example:

Stack 123 contains the config package version v1.0.0 and application package v2.0.0. The next stack, named 124, will
contains the version v1.0.1 for the config and v2.1.0 for the application. Like this we never have to worry if the v1.0.0
of the configuration works with the new application.

Usage (CLI)
===========
Gachette is wrapping around some Fabric scripts. To see the list of commands available, run this:

    $ gachette -l
    Available commands:

        add_to_stack  Add created package to stack and reference packages.
        build         Build the package for the working copy remotely via trebuchet.
        prepare       Prepare the working copy remotely for the project.
        show_config   Dummp settings.
        stack_create  Create a new stack. From old one if specified.
        version

First we create the stack in a certain location. Note that the stack can be anything (semantic version or tag/name):

    gachette -H hero@192.168.1.5 stack_create:foobar1,/var/gachette

From now on, you can add as many as packages as you want for this stack, even overwrite a version of a certain package
by a new one.
We clone the repository and checkout a specific branch:

    gachette -H hero@192.168.1.5 prepare:test_config_first_build,git@github.com:ops-config/test_config,master

Now we build the packages (note: the name `test_config_first_build` is use as a key). Location where the packages should end up is specify:

    gachette -H hero@192.168.1.5 build:test_config_first_build,/var/gachette/debs

Now adding a package to the stack. We need to specify the package information as they came from the last command:

    gachette -H hero@192.168.1.5 add_to_stack:dh-secret-sauce-live,1.0.0,dh-secret-sauce-live-1.0.0-all.deb,/var/gachette,foobar1


Configuration (CLI)
===================
To avoid repeating settings, you can use a dotted configuration file `~/.gachetterc`. It is based on the Fabric one, you can see
the documentation there: http://fabric.readthedocs.org/en/latest/usage/fab.html#settings-files

For example:

    $ cat ~/.gachetterc 
    user=vagrant
    build_host=0.0.0.0

Which will allow you to remove the `-H vagrant@0.0.0.0` option when calling `gachette`.

There is a command to initialize the file, just do `gachette init_config` and it will create the file (with some comments) if it doesn't exist.


Todo
====
* Able to create nested settings from the .gachetterc file (for project configuration).
* handle version by using the git commit hash.
* error handling.
* link the package creation and the stack addition (other than webcallback).
* clean up test and documentation