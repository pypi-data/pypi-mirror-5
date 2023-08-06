# -*- coding: utf-8 -*-

"""
Tests for the text processor.
"""
from __future__ import unicode_literals
import json
from unittest import TestCase, main
from datetime import datetime
from nose.tools import *  # PEP8 asserts
from text.compat import PY2, text_type, unicode
import text.blob as tb
from text.np_extractor import ConllExtractor, FastNPExtractor


class WordListTest(TestCase):

    def setUp(self):
        self.words = 'Beautiful is better than ugly'.split()
        self.mixed = ['dog', 'dogs', 'blob', 'Blobs', 'text']

    def test_len(self):
        wl = tb.WordList(['Beautiful', 'is', 'better'])
        assert_equal(len(wl), 3)

    def test_slicing(self):
        wl = tb.WordList(self.words)
        first = wl[0]
        assert_true(isinstance(first, tb.Word))
        assert_equal(first, 'Beautiful')

        dogs = wl[0:2]
        assert_true(isinstance(dogs, tb.WordList))
        assert_equal(dogs, tb.WordList(['Beautiful', 'is']))

    def test_repr(self):
        wl = tb.WordList(['Beautiful', 'is', 'better'])
        if PY2:
            assert_equal(repr(wl), "WordList([u'Beautiful', u'is', u'better'])")
        else:
            assert_equal(repr(wl), "WordList(['Beautiful', 'is', 'better'])")

    def test_singularize(self):
        wl = tb.WordList(['dogs', 'cats', 'buffaloes', 'men', 'mice'])
        assert_equal(wl.singularize(), ['dog', 'cat', 'buffalo', 'man', 'mouse'
                     ])

    def test_pluralize(self):
        wl = tb.WordList(['dog', 'cat', 'buffalo'])
        assert_equal(wl.pluralize(), ['dogs', 'cats', 'buffaloes'])

    def test_upper(self):
        wl = tb.WordList(self.words)
        assert_equal(wl.upper(), tb.WordList([w.upper() for w in self.words]))

    def test_lower(self):
        wl = tb.WordList(['Zen', 'oF', 'PYTHON'])
        assert_equal(wl.lower(), tb.WordList(['zen', 'of', 'python']))

    def test_count(self):
        wl = tb.WordList(['monty', 'python', 'Python', 'Monty'])
        assert_equal(wl.count('monty'), 2)
        assert_equal(wl.count('monty', case_sensitive=True), 1)
        assert_equal(wl.count('mon'), 0)


class SentenceTest(TestCase):

    def setUp(self):
        self.raw_sentence = \
            'Any place with frites and Belgian beer has my vote.'
        self.sentence = tb.Sentence(self.raw_sentence)

    def test_repr(self):
        assert_equal(repr(self.sentence),
                     "Sentence('{0}')".format(self.raw_sentence))

    def test_stripped_sentence(self):
        assert_equal(self.sentence.stripped,
                     'any place with frites and belgian beer has my vote')

    def test_len(self):
        assert_equal(len(self.sentence), len(self.raw_sentence))

    def test_dict(self):
        sentence_dict = self.sentence.dict
        assert_equal(sentence_dict, {
            'raw': self.raw_sentence,
            'start_index': 0,
            'sentiment': (0.0, 0.0),
            'end_index': len(self.raw_sentence) - 1,
            'stripped': 'any place with frites and belgian beer has my vote',
            'noun_phrases': self.sentence.noun_phrases,
            })

    def test_pos_tags(self):
        then1 = datetime.now()
        tagged = self.sentence.pos_tags
        now1 = datetime.now()
        t1 = now1 - then1

        then2 = datetime.now()
        tagged = self.sentence.pos_tags
        now2 = datetime.now()
        t2 = now2 - then2

        # Getting the pos tags the second time should be faster
        # because they were stored as an attribute the first time
        assert_true(t2 < t1)
        assert_equal(tagged,
                [('Any', 'DT'), ('place', 'NN'), ('with', 'IN'),
                ('frites', 'NNS'), ('and', 'CC'), ('Belgian', 'JJ'),
                ('beer', 'NN'), ('has', 'VBZ'), ('my', 'PRP$'),
                ('vote', 'NN')]
        )

    def test_noun_phrases(self):
        nps = self.sentence.noun_phrases
        assert_equal(nps, ['belgian beer'])

    def test_words_are_word_objects(self):
        words = self.sentence.words
        assert_true(isinstance(words[0], tb.Word))
        assert_equal(words[1].pluralize(), 'places')


class TextBlobTest(TestCase):

    def setUp(self):
        self.text = \
            """Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!"""
        self.blob = tb.TextBlob(self.text)

        self.np_test_text = '''
Python is a widely used general-purpose, high-level programming language.
Its design philosophy emphasizes code readability, and its syntax allows
programmers to express concepts in fewer
lines of code than would be possible in languages such as C.
The language provides constructs intended to enable clear programs on both a small and large scale.
Python supports multiple programming paradigms, including object-oriented,
imperative and functional programming or procedural styles.
It features a dynamic type system and automatic memory management and
has a large and comprehensive standard library. Like other dynamic languages, Python is often used as a scripting language,
but is also used in a wide range of non-scripting contexts.
Using third-party tools, Python code can be packaged into standalone executable
programs. Python interpreters are available for many operating systems. CPython, the reference implementation of Python, is free and open source software and h
as a community-based development model, as do nearly all of its alternative implementations. CPython
is managed by the non-profit Python Software Foundation.'''
        self.np_test_blob = tb.TextBlob(self.np_test_text)

        self.short = "Beautiful is better than ugly. "
        self.short_blob = tb.TextBlob(self.short)

    def tearDown(self):
        pass

    def test_init(self):
        blob = tb.TextBlob('Wow I love this place. It really rocks my socks!!!')
        assert_equal(len(blob.sentences), 2)
        assert_equal(blob.sentences[1].stripped, 'it really rocks my socks')
        assert_equal(blob.string, blob.raw)

        # Must initialize with a string
        assert_raises(TypeError, tb.TextBlob.__init__, ['invalid'])

    def test_sentences(self):
        blob = self.blob
        assert_equal(len(blob.sentences), 19)
        assert_true(isinstance(blob.sentences[0], tb.Sentence))

    def test_iter(self):
        for i, letter in enumerate(self.short_blob):
            assert_equal(letter, self.short[i])

    def test_raw_sentences(self):
        blob = tb.TextBlob(self.text)
        assert_equal(len(blob.raw_sentences), 19)
        assert_equal(blob.raw_sentences[0], "Beautiful is better than ugly.")

    def test_blob_with_no_sentences(self):
        text = "this isn't really a sentence it's just a long string of words"
        blob = tb.TextBlob(text)
        # the blob just has one sentence
        assert_equal(len(blob.sentences), 1)
        # the start index is 0, the end index is len(text) - 1
        assert_equal(blob.sentences[0].start_index, 0)
        assert_equal(blob.sentences[0].end_index, len(text) - 1)

    def test_len(self):
        blob = tb.TextBlob('lorem ipsum')
        assert_equal(len(blob), len('lorem ipsum'))

    def test_repr(self):
        blob1 = tb.TextBlob('lorem ipsum')
        assert_equal(repr(blob1), "TextBlob('lorem ipsum')")
        big_blob = tb.TextBlob(self.text)
        assert_equal(repr(big_blob),
                     "TextBlob('Beautiful is better than ugly.\nExplicit ...'s do more of those!')"
                     )

    def test_cmp(self):
        blob1 = tb.TextBlob('lorem ipsum')
        blob2 = tb.TextBlob('lorem ipsum')
        blob3 = tb.TextBlob('dolor sit amet')

        assert_true(blob1 == blob2)  # test ==
        assert_true(blob1 > blob3)  # test >
        assert_true(blob3 < blob2)  # test <

    def test_words(self):
        blob = \
            tb.TextBlob('Beautiful is better than ugly. Explicit is better than implicit.'
                     )
        assert_true(isinstance(blob.words, tb.WordList))
        assert_equal(blob.words, tb.WordList([
            'Beautiful',
            'is',
            'better',
            'than',
            'ugly',
            'Explicit',
            'is',
            'better',
            'than',
            'implicit',
            ]))

    def test_pos_tags(self):
        blob = tb.TextBlob('Simple is better than complex. '
                            'Complex is better than complicated.')
        assert_equal(blob.pos_tags, [
            ('Simple', 'NN'),
            ('is', 'NNS'),
            ('better', 'JJR'),
            ('than', 'IN'),
            ('complex', 'NN'),
            ('Complex', 'NNP'),
            ('is', 'VBZ'),
            ('better', 'RBR'),
            ('than', 'IN'),
            ('complicated', 'VBN'),
            ])

    def test_np_extractor_defaults_to_conll2000(self):
        text = "Python is a high-level scripting language."
        blob1 = tb.TextBlob(text)
        print(blob1.noun_phrases)  # Lazy loads the extractor
        assert_true(isinstance(blob1.np_extractor, FastNPExtractor))

    def test_np_extractor_is_shared_among_instances(self):
        blob1 = tb.TextBlob("This is one sentence")
        blob2 = tb.TextBlob("This is another sentence")
        assert_true(blob1.np_extractor is blob2.np_extractor)

    def test_can_use_different_np_extractors(self):
        e = ConllExtractor()
        text = "Python is a high-level scripting language."
        blob = tb.TextBlob(text)
        blob.np_extractor = e
        print(blob.noun_phrases)
        assert_true(isinstance(blob.np_extractor, ConllExtractor))

    def test_getitem(self):
        blob = tb.TextBlob('lorem ipsum')
        assert_equal(blob[0], 'l')
        assert_equal(blob[0:5], tb.TextBlob('lorem'))

    def test_upper(self):
        blob = tb.TextBlob('lorem ipsum')
        assert_true(is_blob(blob.upper()))
        assert_equal(blob.upper(), tb.TextBlob('LOREM IPSUM'))

    def test_upper_and_words(self):
        blob = tb.TextBlob('beautiful is better')
        assert_equal(blob.upper().words, tb.WordList(['BEAUTIFUL', 'IS', 'BETTER'
                     ]))

    def test_lower(self):
        blob = tb.TextBlob('Lorem Ipsum')
        assert_true(is_blob(blob.lower()))
        assert_equal(blob.lower(), tb.TextBlob('lorem ipsum'))

    def test_find(self):
        text = 'Beautiful is better than ugly.'
        blob = tb.TextBlob(text)
        assert_equal(blob.find('better', 5, len(blob)), text.find('better', 5,
                     len(text)))

    def test_rfind(self):
        text = 'Beautiful is better than ugly. '
        blob = tb.TextBlob(text)
        assert_equal(blob.rfind('better'), text.rfind('better'))

    def test_startswith(self):
        blob = tb.TextBlob(self.text)
        assert_true(blob.startswith('Beautiful'))
        assert_true(blob.starts_with('Beautiful'))

    def test_endswith(self):
        blob = tb.TextBlob(self.text)
        assert_true(blob.endswith('of those!'))
        assert_true(blob.ends_with('of those!'))

    def test_split(self):
        blob = tb.TextBlob('Beautiful is better')
        assert_equal(blob.split(), tb.WordList(['Beautiful', 'is', 'better']))

    def test_title(self):
        blob = tb.TextBlob('Beautiful is better')
        assert_equal(blob.title(), tb.TextBlob('Beautiful Is Better'))

    def test_format(self):
        blob = tb.TextBlob('1 + 1 = {0}')
        assert_equal(blob.format(1 + 1), tb.TextBlob('1 + 1 = 2'))
        assert_equal('1 + 1 = {0}'.format(tb.TextBlob('2')), '1 + 1 = 2')

    def test_indices(self):
        blob = tb.TextBlob(self.text)
        first_sentence = blob.sentences[0]
        second_sentence = blob.sentences[1]
        last_sentence = blob.sentences[len(blob.sentences) - 1]
        assert_equal(first_sentence.start_index, 0)
        assert_equal(first_sentence.end_index, 30)

        assert_equal(second_sentence.start_index, 30)
        assert_equal(second_sentence.end_index, 63)

        assert_equal(last_sentence.start_index, 740)
        assert_equal(last_sentence.end_index, 804)

    def test_indices_short_names(self):
        blob = tb.TextBlob(self.text)
        last_sentence = blob.sentences[len(blob.sentences) - 1]
        assert_equal(last_sentence.start, 740)
        assert_equal(last_sentence.end, 804)

    def test_replace(self):
        blob = tb.TextBlob('textblob is a blobby blob')
        assert_equal(blob.replace('blob', 'bro'),
                     tb.TextBlob('textbro is a broby bro'))
        assert_equal(blob.replace('blob', 'bro', 1),
                     tb.TextBlob('textbro is a blobby blob'))

    def test_join(self):
        l = ['explicit', 'is', 'better']
        wl = tb.WordList(l)
        assert_equal(tb.TextBlob(' ').join(l), tb.TextBlob('explicit is better'))
        assert_equal(tb.TextBlob(' ').join(wl), tb.TextBlob('explicit is better'))

    def test_multiple_punctuation_at_end_of_sentence(self):
        '''Test sentences that have multiple punctuation marks
        at the end of the sentence.'''
        blob = tb.TextBlob('Get ready! This has an ellipses...')
        assert_equal(len(blob.sentences), 2)
        assert_equal(blob.sentences[1].raw, 'This has an ellipses...')
        blob2 = tb.TextBlob('OMG! I am soooo LOL!!!')
        assert_equal(len(blob2.sentences), 2)
        assert_equal(blob2.sentences[1].raw, 'I am soooo LOL!!!')

    def test_blob_noun_phrases(self):
        noun_phrases = self.np_test_blob.noun_phrases
        assert_true('python' in noun_phrases)
        assert_true('design philosophy' in noun_phrases)

    def test_word_counts(self):
        blob = tb.TextBlob('Buffalo buffalo ate my blue buffalo.')
        assert_equal(blob.word_counts['buffalo'], 3)
        assert_equal(blob.words.count('buffalo'), 3)
        assert_equal(blob.words.count('buffalo', case_sensitive=True), 2)
        assert_equal(blob.word_counts['blue'], 1)
        assert_equal(blob.words.count('blue'), 1)
        assert_equal(blob.word_counts['ate'], 1)
        assert_equal(blob.words.count('ate'), 1)
        assert_equal(blob.word_counts['buff'], 0)
        assert_equal(blob.words.count('buff'), 0)

        blob2 = tb.TextBlob(self.text)
        assert_equal(blob2.words.count('special'), 2)
        assert_equal(blob2.words.count('special', case_sensitive=True), 1)

    def test_np_counts(self):
        # Add some text so that we have a noun phrase that
        # has a frequency greater than 1
        noun_phrases = self.np_test_blob.noun_phrases
        assert_equal(noun_phrases.count('python'), 6)
        assert_equal(noun_phrases.count('cpython'), 2)
        assert_equal(noun_phrases.count('not found'), 0)

    def test_add(self):
        blob1 = tb.TextBlob('Hello, world! ')
        blob2 = tb.TextBlob('Hola mundo!')
        # Can add two text blobs
        assert_equal(blob1 + blob2, tb.TextBlob('Hello, world! Hola mundo!'))
        # Can also add a string to a tb.TextBlob
        assert_equal(blob1 + 'Hola mundo!',
                     tb.TextBlob('Hello, world! Hola mundo!'))
        # Or both
        assert_equal(blob1 + blob2 + ' Goodbye!',
                     tb.TextBlob('Hello, world! Hola mundo! Goodbye!'))

        # operands must be strings
        assert_raises(TypeError, blob1.__add__, ['hello'])

    def test_unicode(self):
        blob = tb.TextBlob(self.text)
        assert_equal(str(blob), str(self.text))

    def test_strip(self):
        text = 'Beautiful is better than ugly. '
        blob = tb.TextBlob(text)
        assert_true(is_blob(blob))
        assert_equal(blob.strip(), tb.TextBlob(text.strip()))

    def test_strip_and_words(self):
        blob = tb.TextBlob('Beautiful is better! ')
        assert_equal(blob.strip().words, tb.WordList(['Beautiful', 'is', 'better'
                     ]))

    def test_index(self):
        blob = tb.TextBlob(self.text)
        assert_equal(blob.index('Namespaces'), self.text.index('Namespaces'))

    def test_sentences_after_concatenation(self):
        blob1 = tb.TextBlob('Beautiful is better than ugly. ')
        blob2 = tb.TextBlob('Explicit is better than implicit.')

        concatenated = blob1 + blob2
        assert_equal(len(concatenated.sentences), 2)

    def test_sentiment(self):
        positive = tb.TextBlob('This is the best, most amazing '
                            'text-processing library ever!')
        assert_true(positive.sentiment[0] > 0.0)
        negative = tb.TextBlob("bad bad bitches that's my muthufuckin problem.")
        assert_true(negative.sentiment[0] < 0.0)
        zen = tb.TextBlob(self.text)
        assert_equal(round(zen.sentiment[0], 1), 0.2)
        assert_equal(round(zen.sentiment[1], 1), 0.6)

    def test_bad_init(self):
        assert_raises(TypeError, tb.TextBlob.__init__, ['bad'])

    def test_in(self):
        blob = tb.TextBlob('Beautiful is better than ugly. ')
        assert_true('better' in blob)
        assert_true('fugly' not in blob)

    def test_json(self):
        blob = tb.TextBlob('Beautiful is better than ugly. ')
        blob_dict = json.loads(blob.json)[0]
        assert_equal(blob_dict['stripped'], 'beautiful is better than ugly')
        assert_equal(blob_dict['noun_phrases'], blob.sentences[0].noun_phrases)
        assert_equal(blob_dict['start_index'], blob.sentences[0].start)
        assert_equal(blob_dict['end_index'], blob.sentences[0].end)
        assert_almost_equal(blob_dict['sentiment'][0],
                            blob.sentences[0].sentiment[0], places=4)

    def test_words_are_word_objects(self):
        words = self.blob.words
        assert_true(isinstance(words[0], tb.Word))

    def test_words_have_pos_tags(self):
        blob = tb.TextBlob('Simple is better than complex. '
                            'Complex is better than complicated.')
        first_word, first_tag = blob.pos_tags[0]
        assert_true(isinstance(first_word, tb.Word))
        assert_equal(first_word.pos_tag, first_tag)


class WordTest(TestCase):

    def setUp(self):
        self.cat = tb.Word('cat')
        self.cats = tb.Word('cats')

    def test_init(self):
        tb.Word("cat")
        assert_true(isinstance(self.cat, tb.Word))
        word = tb.Word('cat', 'NN')
        assert_equal(word.pos_tag, 'NN')

    def test_singularize(self):
        singular = self.cats.singularize()
        assert_equal(singular, 'cat')
        assert_true(isinstance(singular, unicode))
        assert_equal(self.cat.singularize(), 'cat')

    def test_pluralize(self):
        plural = self.cat.pluralize()
        assert_equal(self.cat.pluralize(), 'cats')
        assert_true(isinstance(plural, unicode))

    def test_repr(self):
        assert_equal(repr(self.cat), "Word('cat')")

    def test_str(self):
        assert_equal(str(self.cat), 'cat')

    def test_has_str_methods(self):
        assert_equal(self.cat.upper(), "CAT")
        assert_equal(self.cat.lower(), "cat")
        assert_equal(self.cat[0:2], 'ca')


def is_blob(obj):
    return isinstance(obj, tb.TextBlob)


if __name__ == '__main__':
    main()
