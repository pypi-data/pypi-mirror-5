Logging
=======

You can use Python's `logging <http://docs.python.org/library/logging.html>`_
module to see py-textteaser's HTTP requests and responses.

First, set up the logger with the DEBUG level:

.. code-block:: python

    >>> import logging
    >>>
    >>> logger = logging.getLogger('textteaser')
    >>> logger.setLevel(logging.DEBUG)

Then set up the formatter and a handler:

.. code-block:: python

    >>> formatter = logging.Formatter('%(name)s-%(levelname)s: %(message)s')
    >>> handler = logging.StreamHandler()
    >>> handler.setFormatter(formatter)
    >>> logger.addHandler(handler)

Now when you make a request:

.. code-block:: python

    >>> tt = textteaser.TextTeaser('foobarbaz')
    >>> tt.summarize(url='https://en.wikipedia.org/wiki/Alan_turing')

the HTTP request and response will be logged:

.. code-block:: python

    >>> textteaser.textteaser.TextTeaser-DEBUG: posting to url:
        https://textteaser.p.mashape.com/api with data: {
            'url': 'https://en.wikipedia.org/wiki/Alan_turing',
            'text': None,
            'title': None
        }
        textteaser.textteaser.TextTeaser-DEBUG: received response: {
            u'title': u'Wikipedia, the free encyclopedia',
            u'summaryId': u'3wbgVQ',
            u'sentences': [
                u'He went on to prove that there was no solution to the]
                    Entscheidungsproblem by first showing that the halting
                    problem for Turing machines is undecidable: in general,
                    it is not possible to decide algorithmically whether a
                    given Turing machine will ever halt.',
                u"It was also novel in its notion of a 'Universal Machine' (now
                    known as a Universal Turing machine), with the idea that
                    such a machine could perform the tasks of any other
                    machine, or in other words, it is provably capable of
                    computing anything that is computable.",
                u'30 In June 1938, he obtained his PhD from Princeton; 31 his
                    dissertation, Systems of Logic Based on Ordinals, 32 33
                    introduced the concept of ordinal logic and the notion of
                    relative computing, where Turing machines are augmented
                    with so-called oracles, allowing a study of problems that
                    cannot be solved by a Turing machine.',
                u'115\n\nIn 1999, Time Magazine named Turing as one of the 100
                    Most Important People of the 20th century and stated: "The
                    fact remains that everyone who taps at a keyboard, opening
                    a spreadsheet or a word-processing program, is working on
                    an incarnation of a Turing machine." 3 Turing is featured
                    in the 1999 Neal Stephenson novel Cryptonomicon.',
                u'On 23 June 2012, Google featured an interactive doodle where
                    visitors had to change the instructions of a Turing
                    Machine, so when run, the symbols on the tape would match
                    a provided sequence, featuring "Google" in Baudot-Murray
                    code.'
            ]
        }

