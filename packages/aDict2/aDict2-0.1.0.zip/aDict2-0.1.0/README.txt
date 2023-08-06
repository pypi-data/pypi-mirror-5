=====
aDict
=====

aDict provides interface to reading and writing aDict dictionary format.
Typical usage::

    from adict import *                # data classes
    from adict.parser import Parser    # text to data
    from adict.printer import Printer  # data to text
    
    with open('some file') as f:
        a = Article('Python')
        a.classes.append('n')
        a.transcriptions.append('ˈpaɪθən')
        d1 = Definition('a kind of programming language')
        d2 = Definition('a kind of Snake')
        d2.links.append('hyperonym', 'Snake')
        a.content = [d1, d2]
        
        dictionary = Parser(f).parse()
        dictionary.articles.append(a)
    
    with open('some other file', 'w') as f:
        f.write(str(Printer(dictionary)))

aDict format specification
==========================

…in English has not written yet. :)

However, I think, this format is pretty simple to understand by trial and error or by looking on this implementation.


Contributors
============

Only me = arseniiv so far.
