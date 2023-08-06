Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
Description: ********************************************
        marshmallow: Simplified Object Serialization
        ********************************************
        
        .. image:: https://badge.fury.io/py/marshmallow.png
            :target: http://badge.fury.io/py/marshmallow
            :alt: Latest version
        
        .. image:: https://travis-ci.org/sloria/marshmallow.png?branch=master
            :target: https://travis-ci.org/sloria/marshmallow
            :alt: Travis-CI
        
        Homepage: http://marshmallow.readthedocs.org/
        
        
        **marshmallow** is an ORM/ODM/framework-agnostic library for converting complex datatypes, such as objects, into native Python datatypes. The serialized objects can then be rendered to standard formats such as JSON for use in a REST API.
        
        .. code-block:: python
        
            from datetime import datetime
            from marshmallow import Serializer, fields
        
            # A "model"
            class Person(object):
                def __init__(self, name):
                    self.name = name
                    self.date_born = datetime.now()
        
            # A serializer
            class PersonSerializer(Serializer):
                name = fields.String()
                date_born = fields.DateTime()
        
            person = Person("Guido van Rossum")
            serialized = PersonSerializer(person)
            serialized.data
            # {"name": "Guido van Rossum", "date_born": "Sun, 10 Nov 2013 14:24:50 -0000"}
        
        
        Get It Now
        ==========
        
        ::
        
            $ pip install -U marshmallow
        
        
        Documentation
        =============
        
        Full documentation is available at http://marshmallow.readthedocs.org/ .
        
        
        Requirements
        ============
        
        - Python >= 2.7 or >= 3.3
        
        
        License
        =======
        
        MIT licensed. See the bundled `LICENSE <https://github.com/sloria/marshmallow/blob/master/LICENSE>`_ file for more details.
        
        
        Changelog
        ---------
        
        0.1.0 (2013-11-10)
        ++++++++++++++++++
        
        * First release.
        
Keywords: serialization,rest,json,api
Platform: UNKNOWN
Classifier: Development Status :: 2 - Pre-Alpha
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
