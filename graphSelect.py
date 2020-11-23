"""
graphSelect

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

def selectNodeType(g, nodeType) ->str:
    for u, d in list(g.nodes(data=True)):
        if d["type"] == nodeType:
            return d["id"]

def selectNodesType(g, nodeType) ->list:
    nodeList = []
    for u, d in list(g.nodes(data=True)):
        if d["type"] == nodeType:
            nodeList.append(d)
    return nodeList


def selectNodeID(g, key) ->object:
    """
    """
    d: object
    for u, d in list(g.nodes(data=True)):
        if d["id"] == key:
            return d

def countNodeType(g, nodeType) -> int:
    count = 0
    for u, d in list(g.nodes(data=True)):
        if d["type"] == nodeType:
            count = count + 1
    return count

def select(g, query):
    '''Call the query for each edge, return list of matches'''
    result = []
    for u,v,d in g.edges(data=True):
        if query(u,v,d):
            result.append([(u,v)])
    return result



