"""
subset

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import term


class Subset:
    """
    CDISC controlled terminology subset provided as part of an enumerated Conceptual Domain
    """
    def __init__(self, c_code, name):
        """
        :param c_code: subset list concept code
        :param name:  subset list name
        """
        self.c_code = c_code
        self.name = name
        self.terms = []

    def add_term(self, c_code, sub_val, default="No"):
        """
        add a new term to the list of terms in the CT subset
        :param c_code: CT term concept code
        :param sub_val: CT term submission value
        :param default: if the CT term is the default value in this subset
        """
        self.terms.append(term.Term(c_code, sub_val, default))