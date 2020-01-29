======
README
======


Prerequisites
=============

* `Anaconda 4+ <https://www.anaconda.com/>`_
* Internet connection
* Permission to access the website (via CUNET User Account)


Set up environment
==================
* Open ``Anaconda Prompt``

* Go to the root directory of this project. Then create its Conda environment from ``environment.yml`` by entering the following command:
   * ``conda env create -f environment.yml``

* Activate the environment by:
   * ``activate IQNewsClip-Web-Scraper``

* Install packages from ``requirements.txt`` by:
   * ``pip install -r requirements.txt``

* Install the local package by:
   * ``pip install . --no-cache-dir``


Note
====

* To remove the environment:
   * ``activate root``
   * ``conda remove -n IQNewsClip-Web-Scraper --all``


Useful links
============

* `Managing environments <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_
