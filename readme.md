# CribbageCoach
#### Cribbage AI and Tool for Improving Cribbage Game
---

[CribbageCoach Live Site](http://www.cribbagecoach.com)

[Project Write-Up](http://www.cribbagecoach.com/blog)

### Status:

[![Build Status](https://travis-ci.org/alexjohnson84/crib.svg?branch=master)](https://travis-ci.org/alexjohnson84/crib)

Note: Test Suite currently only covers the Business Logic behind the API and validates that the current models load into the a usable form by the application.  It does not test the frontend.  To do so, download the repo and run the following to run automated games against the frontend:

```bash
# start flask application on local server
make play
#in separate terminal tab
make testapp
```


### Overview:
CribbageCoach consists of 3 parts
* Stateless API with Cribbage Logic Built in (gameplay)
* Machine Learning Models w/ artificial (models)
* Frontend Flask Application (app)

If you wish to use this application to run your own experiments, see the
Makefile for some common scripts to generate fake games to help get you started

```bash
make install
source cc_virt/bin/activate
make clean
make generate
```
