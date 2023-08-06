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
        
        A Python library for easily getting user input from multiple items in a list, emulating the bash(1) select builtin function.
        
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
        
        
        =======================
        Version 0.1 (10/31/2013)
        =======================
        * updating setup.py formatting - Matt Behrens http://github.com/askedrelic/pyselect/commit/157d5f932d89abefb491caade959bead8c7a53d8
        * adding manifest - Matt Behrens http://github.com/askedrelic/pyselect/commit/18420069e6de7c3367b17c3882437c90b534d786
        * add history - Matt Behrens http://github.com/askedrelic/pyselect/commit/b85b11d2ae3011a18dcadcf145cb543e2ec30f45
        * start testing - Matt Behrens http://github.com/askedrelic/pyselect/commit/c09e02bac7d09388246fc4a2b16e71662099cfdf
        * add history, readme - Matt Behrens http://github.com/askedrelic/pyselect/commit/5fced5a9b0916c173c4a7f5e0c199ed0b3935c41
        * add readme - Matt Behrens http://github.com/askedrelic/pyselect/commit/a2fd5efeb7e8edc2dc175bc7e737ebd444c1cd23
        * add license - Matt Behrens http://github.com/askedrelic/pyselect/commit/dafb20c50258415a91433ee5a6bda7910b433df1
        * lets call it 0.1 - Matt Behrens http://github.com/askedrelic/pyselect/commit/2ff14ca7db13f50fd2a469a32c2cf1c3d3188448
        
Platform: UNKNOWN
Classifier: Intended Audience :: Developers
Classifier: Natural Language :: English
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Topic :: Software Development :: Libraries :: Python Modules
