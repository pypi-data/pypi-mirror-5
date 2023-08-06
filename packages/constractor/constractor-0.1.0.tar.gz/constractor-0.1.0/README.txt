===========
constractor
===========

Constractor (derived from "Content Extractor') allows one to use machine learning for web pages content extraction.
Library provide following functionality:

* Extendable features api.
* Gui tools for simple train-set creation.
* Simple training and testing process.
* Simple usage of trained model.
* Models dumping.
* etc

Installation
============

NOTE: Project was developed and tested under Ubuntu 12.04. Other operation systems may require enhancements of library.

Ubuntu >=12.04 instructions:

* Install apt dependecies: ``sudo apt-get install pip gcc g++ python-dev python-qt4``

* Install constractor: ``sudo pip install constractor``

Usage
=====

Following code will run gui train helper::

    #!/usr/bin/env python
    from constractor.train import GuiTrainer

    if __name__ == '__main__':
        GuiTrainer()

And following code will print html of predicted element in DOM::

    #!/usr/bin/env python
    from constractor.parser import Parser

    if __name__ == '__main__':
        predicted = Parser('https://pypi.python.org', model_file='model.txt').predicted
        for element in predicted:
            print unicode(element.toInnerXml()).encode('utf-8')

Contribution
============

Project is completely open for contribution. See more on bitbucket repo: https://bitbucket.org/dkuryakin/constractor