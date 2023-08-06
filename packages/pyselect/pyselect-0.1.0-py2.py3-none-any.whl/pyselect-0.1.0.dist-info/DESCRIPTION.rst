Copyright (c) 2013 Matt Behrens <askedrelic@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Description: ========
        pyselect
        ========
        
        A Python library for easily getting user input form multiple items in a list, emulating the Bash(1) builtin select.
        
        ============
        Usage
        ============
        
        Pyselect wraps raw_input, more or less::
        
            In [1]: import pyselect
            In [2]: pyselect.select(['apples', 'oranges', 'bananas'])
            1) apples
            2) oranges
            3) bananas
            #? 2
            Out[2]: 'oranges'
        
        But can also be used as a Python module, when scripting::
        
            $ python -m pyselect $(ls)
            1) LICENSE.txt
            2) build/
            3) dist/
            4) pyselect.egg-info/
            5) pyselect.py
            6) pyselect.pyc
            7) setup.py
            8) test.py
            #? 4
            pyselect.egg-info/
        
        Or in a Bash pipe::
        
            $ ls | xargs python -m pyselect
            1) LICENSE.txt
            2) build/
            3) dist/
            4) pyselect.egg-info/
            5) pyselect.py
            6) pyselect.pyc
            7) setup.py
            8) test.py
            #? 5
            pyselect.py
            
        ============
        Installation
        ============
        
        Pyselect is available on Pypi::
        
            $ pip install pyselect
        
        ============
        License
        ============
        
        MIT, see LICENSE.txt
        
        
        
Platform: UNKNOWN
Classifier: Intended Audience :: Developers
Classifier: Natural Language :: English
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Topic :: Software Development :: Libraries :: Python Modules
