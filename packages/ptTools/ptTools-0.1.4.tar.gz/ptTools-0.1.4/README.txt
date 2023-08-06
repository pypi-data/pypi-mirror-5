
.. _start:

=====================
README for ptTools.py
=====================

.. _intro:

The ptTools packages provides a domain specific language, for
pattern matching on trees - python parsetrees in particular.

Matching parsetree nodes instead of regular expression based string
search, allows fine-grained, semantic control over search results.
The second major benefit is that the matches are instantiated
parsetree nodes, that can be manipulated and recompiled.  Parsetree
based search is of interest especially when manipulating or
substituting selected nodes, e.g. for testing, or code analysis.

The domain specific language of ptTools patterns consists of a family
of pattern objects, all of which can be expressed in valid python
code.  Binary and unary operators similar to those of regular
expressions are available. The resulting pattern language resembles
the grammar rules it matches.

Emphasis was put on an intuitive interface, and a clean and easily
extensible object-oriented design.  The components are loosely
coupled.  For example the pattern objects can be matched against
tuples as well as against attributed parsetree nodes.  The parsetree
nodes may or may not hold references to tokens, which again may or may
not be attributed.




.. _contents:

**Contents**

    * Two simple examples_
    * Description of the available operators_ (**TODO**)
    * References_
    * License_

..  * A few implementation_ notes (**TODO**)
..  * A todo_ list (**TODO**)


.. _location:

ptTools was written by Markus Rother (python@markusrother.de) and is
located at http://github.com/941design/pttools.  Feedback and
suggestions are welcome.  ptTools requires python3.2.

The object-oriented design of the RegularLanguageAcceptor classes in
``ptTools.misc.acceptors`` was inspired by Lukas Renggli's `Petit
Parser <http://www.lukas-renggli.ch/blog/petitparser-1>`_ written in
Smalltalk.

.. _examples:
.. _`previous example`:
.. _`for_stmt`:

A first example - Creating a simple pattern
===========================================

 The following first example matches a for loop in a python source file.
 We will first `create the parsetree`_ as a nested tuple, then
 `create the pattern`_, and finally we will `match the pattern`_
 against the parsetree.

 Our starting point is the corresponding grammar rule, taken from
 http://docs.python.org/3.2/reference/grammar.html:
 ::

    for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]

 Lowercase expressions are non-terminals that can be imported from the
 ``symbol`` module.  Strings represent terminals with a string value.
 Bracketed sub-rules are optional.  For the sake of simplicity we
 disregard the else option in our pattern.  Also, we will replace the
 rules ``exprlist``, ``testlist`` and ``suite`` by wildcards.  


.. _`create the parsetree`:

Creating the parse tree
~~~~~~~~~~~~~~~~~~~~~~~

 Here, the parse tree is created from a short source segment.  The
 result is a nested tuple of the form:
 ::

    node ::= (INT (, (node|STR))*)

 >>> import parser
 ...
 >>> source = '''
 ... for k in range(10):
 ...     print(k)
 ... '''
 >>> root = parser.suite(source).totuple()

 Note, that the ``for_stmt`` non-terminal seen in the rule above, is
 not the grammar's start symbol, but will be nested somewhere in the
 tuple.


.. _`create the pattern`:

Creating a pattern
~~~~~~~~~~~~~~~~~~

 Next, we create a pattern that matches any for-statement without the
 else option.  As a universal wildcard pattern, we instantiate an
 ``AnyPattern()`` and assign it to the underscore.  The ``TuplePattern`` is
 - as the name suggests - a pattern that matches tuples.  It may hold
 other patterns or literal values.
 
 >>> from symbol import for_stmt
 >>> from ptTools.ptpatterns import TuplePattern as Tup
 >>> from ptTools.ptpatterns import AnyPattern as Any
 >>> _ = Any()
 ...
 >>> pattern = Tup(for_stmt, 'for', _, 'in', _, ':', _)
 >>> pattern
 (296, (1, 'for'), _, (1, 'in'), _, (11, ':'), _)

 where the integers originate from the ``symbol`` and ``token`` modules.

 >>> import symbol
 >>> import token
 >>> 296==symbol.for_stmt and 1==token.NAME and 11==token.COLON
 True

 Repeated for comparison:  The rule
 ::

    for_stmt: 'for' exprlist 'in' testlist ':' suite

 is matched by:
 ::

    ```TuplePattern(for_stmt, 'for', _, 'in', _, ':', _)```

 represented as:
 ::

    ```(296, (1, 'for'), _, (1, 'in'), _, (11, ':'), _)```

 Note, that string literals in the pattern declaration are replaced by
 ``TuplePattern`` instances matching the appropriate parsetree nodes.
 If a token  exists, whose string value equals the given string, that
 token's identifier is inserted, otherwise the identifier defaults to
 ``token.NAME``.
 In the above example ``':'`` was replaced by
 ``TuplePattern(token.COLON, ':')``, because the colon exists as a token.
 The fact that ``in`` and ``for`` are keywords, does not mean they do
 exist as tokens, too.


.. _`match the pattern`:

Matching the pattern
~~~~~~~~~~~~~~~~~~~~

 As mentioned earlier, the pattern does not match the entire parsetree.

 >>> pattern.matches(root)
 False

 It does however match somewhere in the parsetree.

 >>> pattern.matches_in(root)
 True
 >>> match = pattern.first_match_in(root)
 >>> isinstance(match, tuple)
 True

 We can retrieve the matched node, but formatting was lost during
 parsing:

 >>> from ptTools.parsetree import tupletraversal 
 >>> ' '.join([s for s in tupletraversal.leaves(match)])
 'for k in range ( 10 ) :   print ( k )  '


.. _`another example`:
.. _`classdef`:

Example two - Processing matched nodes
======================================

 This example demonstrates a slightly more complex pattern
 description, that matches any class definition in python source.  The
 example also shows how to capture matched regions, and apply
 functions to subpatterns.


Pattern definition
~~~~~~~~~~~~~~~~~~

 >>> from symbol import classdef
 >>> from token import NAME
 >>> import ptTools
 >>> from ptTools.ptpatterns import TuplePattern as Tup
 >>> from ptTools.ptpatterns import _
 ...
 >>> pattern = Tup(classdef, 'class', (NAME, _), ['(', [ _ ], ')'], ':', _)

 Compare this pattern to the grammar rule definition of ``classdef`` taken from
 http://docs.python.org/3.2/reference/grammar.html:
 :: 

  classdef: 'class' NAME ['(' [arglist] ')'] ':' suite

 Unless we are interested in the class definition's body, we may
 replace the pattern's tail with another wildcard:

 >>> more = ~_ ## Creating a Kleene Closure over Any().
 ...
 >>> pattern = Tup(classdef, 'class', (NAME, _), more)

..  (Under operators, see `Kleene closure`_).


Adding callback functions
~~~~~~~~~~~~~~~~~~~~~~~~~

 To send the matched regions to callback functions, simply append '``%
 callable``' to a pattern.  For instance, if we would like to print
 the class name from the above example, we would simply write:
 ::

    ```pattern = Tup(classdef, 'class', (NAME, _%print), more)```

 Note, that the left hand side of the ``%`` operator must have been
 evaluated to a PatternObject prior to evaluating the entire
 expression.  If we would like to print the entire terminal node, we
 have to be explicit, and type:
 ::

    ```pattern = Tup(classdef, 'class', Tup(NAME, _)%print, more)```

 Now, assume, one would like to count classes in a module.  For that
 purpose we define an ``inc`` function with the side effect of
 incrementing a counter, and which is to be called every time our
 classdef pattern matches.  All we have to do is to add a callback to
 ``inc`` to the pattern with the ``%`` operator.

 >>> count = 0
 >>> def inc(ignore):
 ...     globals()['count'] += 1
 ...
 >>> pattern = Tup(classdef, 'class', (NAME, _%print), more)%inc

 Note, that this does two things: It prints the classname *and then*
 increments the counter.  The order of the two is determined by the
 traversal order through our parsetree (which is preorder, and hence
 lexical order of the source code).  In other words, ``print`` will be
 called before ``inc``, because the class name is encountered before
 the entire class definition ends.

 Callback functions can be chained (e.g. '``%inc%input``'), and are
 executed in the order of appending.
 

Applying patterns
~~~~~~~~~~~~~~~~~

 As seen in the `previous example`_, PatternObjects have a
 ``.match(node)`` method, that tries to match a parsetree node, and if
 successful applies its callback functions to the matched regions.
 Its return value is ``None``.

 We now appply that method to every node in the parsetree, starting at
 its root.  If the pattern matches in a node, all queued callback
 functions will be called with the matched node as their only
 argument.
 
 >>> cls_lst = []
 ...
 >>> pattern = Tup(classdef, 'class', (NAME, _%cls_lst.append), more)%inc
 >>> pattern
 (329, (1, 'class'), (1, _), ~(_))
 
 >>> root = ptTools.parsetree.fromfile('ptpatterns/ptpatterns.py')
 >>> root.preorder_do(pattern.match)
 ...
 >>> 'TuplePattern' in cls_lst
 True

 Currently, five classes are defined in ``ptTools.ptpatterns.ptpatterns``.

 >>> count
 5


.. _`more examples`:

More examples
=============

 Also, see ``ptTools.examples``:

 * ``ptTools.examples.pycat`` is a colorizer printing python source
   code to the command line.  Performance is worse than that of e.g.
   `pygmentize <http://pygments.org/>`_.  However, it may be a good starting point when
   designing patterns and visualizing their matches in a source file.
  
 * ``ptTools.examples.extract`` demonstrates recompilation of a
   captured segment.

 Both examples are executable.


.. _operators:

Available operators
===================

 **TODO**
 
 Please refer to the examples_.  (Also, see
 ``ptTools.misc.acceptors``).


.. _references:

References
==========

  * For the complete python grammar see:
    http://docs.python.org/3.2/reference/grammar.html

  * Nonterminals can be found in: ``/usr/include/python3.2/graminit.h`` as
    well as in the module: ``symbol``.
  
  * Reference for terminals is found in the modules: ``token`` and
    ``tokenize``.


.. _license:

License
=======

 This program was published under the `GNU GENERAL PUBLIC LICENSE
 <http://www.gnu.org/licenses/gpl-3.0.txt>`_.

