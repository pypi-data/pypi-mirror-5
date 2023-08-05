# -*- coding: utf-8 -*-

'''Wrappers for various units of text.'''
import sys
import json
from collections import Counter

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

from np_extractor import NPExtractor
from decorators import cached_property
from utils import lowerstrip, strip_punc
from inflect import singularize, pluralize
from sentiment import sentiment as _sentiment


class WordList(list):

    '''A list-like collection of words.'''

    def __init__(self, collection):
        super(WordList, self).__init__(collection)
        self._collection = collection

    def __repr__(self):
        '''Returns a string representation for debugging.'''
        class_name = self.__class__.__name__
        if len(self) > 60:
            return '{cls}({beginning}...{end})'.format(cls=class_name,
                    beginning=str(self._collection[:3])[:-1],
                    end=str(self._collection[-3:])[1:])
        else:
            return '{cls}({lst})'.format(cls=class_name, lst=self._collection)

    def __getitem__(self, index):
        '''Returns a string at the given index.'''
        return self._collection[index]  # Just return a string

    def __getslice__(self, i, j):
        '''Returns a new WordList with items i:j.'''
        return self.__class__(list.__getslice__(self, i, j))

    def count(self, s, case_sensitive=False, *args, **kwargs):
        """Get the count of a word or phrase `s` within this WordList.

        Arguments:
        - s: The string to count.
        - case_sensitive: A boolean, whether or not the search is
                             case sensitive.
        """
        if not case_sensitive:
            return [word.lower() for word in self].count(s.lower(), *args,
                    **kwargs)
        return self._collection.count(s, *args, **kwargs)

    def upper(self):
        '''Return a new WordList with each word upper-cased.'''
        return self.__class__([word.upper() for word in self])

    def lower(self):
        '''Return a new WordList with each word lower-cased.'''
        return self.__class__([word.lower() for word in self])

    def singularize(self):
        '''Return the single version of each word in this WordList.'''
        return [singularize(word) for word in self]

    def pluralize(self):
        '''Return the plural version of each word in this WordList.'''
        return [pluralize(word) for word in self]


class BaseBlob(object):

    '''An abstract base class that all text.blob classes will inherit from.
    Includes words, POS tag, NP, and word count properties. Also includes
    basic dunder and string methods for making objects like Python strings.
    '''

    def __init__(self, text):
        '''Create a blob-like object.

        Arguments:
        - text: A string, the text.
        '''
        if not isinstance(text, basestring):
            raise TypeError('The `text` argument passed to `__init__(text)` must be a string.'
                            )
        self.raw = text
        self.stripped = lowerstrip(text)

    def _tokenize(self):
        return word_tokenize(self.raw)

    @cached_property
    def words(self):
        '''Returns list of word tokens.
        '''
        return WordList([strip_punc(word) for word in self._tokenize()
                        if strip_punc(word)])  # Excludes punctuation

    @property
    def sentiment(self):
        '''Returns sentiment scores as a tuple of the form
        `(polarity, subjectivity)` where polarity is in the range [-1.0, 1.0]
        and subjectivity is in the range [0.0, 1.0].
        '''
        return _sentiment(self.raw)

    @cached_property
    def noun_phrases(self):
        extractor = NPExtractor(self.raw)
        return WordList([lowerstrip(phrase) for phrase in extractor.extract()
                        if len(phrase) > 1])

    @cached_property
    def pos_tags(self):
        '''Returns an array of tuples of the form (word, POS tag).

        Example:
            [('At', 'IN'), ('eight', 'CD'), ("o'clock", 'JJ'), ('on', 'IN'),
                    ('Thursday', 'NNP'), ('morning', 'NN')]
        '''
        tokens = word_tokenize(self.stripped)
        return nltk.pos_tag(tokens)

    @cached_property
    def word_counts(self):
        '''Dictionary of word frequencies in this text. Internally
        uses collections.Counter.
        '''
        stripped_words = [lowerstrip(word) for word in self.words]
        return Counter(stripped_words)

    @cached_property
    def np_counts(self):
        '''Dictionary of noun phrase frequencies in this text. Internally
        uses collections.Counter.
        '''
        return Counter(self.noun_phrases)

    def __repr__(self):
        '''Returns a string representation for debugging.'''
        class_name = self.__class__.__name__
        if len(self) > 60:
            return "{cls}('{beginning}...{end}')".format(cls=class_name,
                    beginning=self.raw[:40], end=self.raw[-20:])
        else:
            return "{cls}('{text}')".format(cls=class_name, text=self.raw)

    def __len__(self):
        '''Returns the length of the raw text.'''
        return len(self.raw)

    def __str__(self):
        '''Returns a string representation used in print statements
        or str(my_blob).'''
        return self.raw

    def __iter__(self):
        '''Makes the object iterable as if it were a string,
        iterating through the raw string's characters.
        '''
        return iter(self.raw)

    def __cmp__(self, other):
        '''Compare to another object. Indirectly supports '==', '<', etc.'''
        return cmp(str(self), str(other))

    def __getitem__(self, index):
        '''Returns a  substring. If index is an integer, returns a Python
        string of a single character. If a range is given, e.g. `blob[3:5]`,
        a new instance of the class is returned.
        '''
        if isinstance(index, int):
            return self.raw[index]  # Just return a single character
        else:
            # Return a new blob object
            return self.__class__(self.raw[index])

    def __add__(self, other):
        '''Concatenates two text objects the same way Python strings are
        concatenated.

        Arguments:
        - `other`: a string or a text object
        '''
        if isinstance(other, basestring):
            return TextBlob(str(self) + other)
        elif isinstance(other, BaseBlob):
            return TextBlob(str(self) + str(other))
        else:
            raise ValueError('Operands must be either strings or {0} objects'.format(self.__class__.__name__))

    def __contains__(self, sub):
        '''Implements the `in` keyword like a Python string.'''
        return sub in str(self)

    def find(self, sub, start=0, end=sys.maxint):
        '''Behaves like the built-in str.find() method. Returns an integer,
        the index of the first occurrence of the substring argument sub in the
        sub-string given by [start:end].
        '''
        return str(self).find(sub, start, end)

    def rfind(self, sub, start=0, end=sys.maxint):
        '''Behaves like the built-in str.rfind() method. Returns an integer,
        the index of he last (right-most) occurence of the substring argument
        sub in the sub-sequence given by [start:end].
        '''
        return str(self).rfind(sub, start, end)

    def index(self, sub, start=0, end=sys.maxint):
        '''Like blob.find() but raise ValueError when the substring is not found.
        '''
        return str(self).index(sub, start, end)

    def startswith(self, prefix, start=0, end=sys.maxint):
        """Returns True if the blob starts with the given prefix."""
        return str(self).startswith(prefix, start, end)

    def endswith(self, suffix, start=0, end=sys.maxint):
        """Returns True if the blob ends with the given suffix."""
        return str(self).endswith(suffix, start, end)

    # PEP8 aliases
    starts_with = startswith
    ends_with = endswith

    def title(self):
        """Returns a blob object with the text in title-case."""
        return TextBlob(str(self).title())

    def format(self, *args, **kwargs):
        """Perform a string formatting operation, like the built-in
        `str.format(*args, **kwargs)`. Returns a blob object.
        """
        return TextBlob(str(self).format(*args, **kwargs))

    def split(self, sep=None, maxsplit=sys.maxint):
        """Behaves like the built-in str.split() except returns a
        WordList.
        """
        return WordList(str(self).split(sep, maxsplit))

    def strip(self, chars=None):
        """Behaves like the built-in str.strip([chars]) method. Returns
        an object with leading and trailing whitespace removed.
        """
        return self.__class__(str(self).strip(chars))

    def upper(self):
        """Like str.upper(), returns new object with all upper-cased characters.
        """
        return self.__class__(str(self).upper())

    def lower(self):
        """Like str.lower(), returns new object with all lower-cased characters.
        """
        return self.__class__(str(self).lower())

    def join(self, iterable):
        """Behaves like the built-in `str.join(iterable)` method, except
        returns a blob object.

        Returns a blob which is the concatenation of the strings or blobs
        in the iterable.
        """
        return self.__class__(str(self).join(iterable))

    def replace(self, old, new, count=sys.maxint):
        """Return a new blob object with all the occurence of `old` replaced
        by `new`.
        """
        return self.__class__(str(self).replace(old, new, count))


class TextBlob(BaseBlob):

    """A general text block, meant for larger bodies of text (esp. those
    containing sentences.
    """

    def __init__(self, blob):
        '''Initialize a textblob.

        Arguments:
        - `blob`: a string
        '''
        super(TextBlob, self).__init__(blob)

    @cached_property
    def sentences(self):
        '''List of Sentence objects.'''
        return TextBlob.create_sentence_objects(self.raw)

    @property
    def raw_sentences(self):
        '''List of strings, the raw sentences in the blob.'''
        return [sentence.raw for sentence in self.sentences]

    @property
    def serialized(self):
        '''Returns a list of each sentences dict representation.'''
        return [sentence.dict for sentence in self.sentences]

    @property
    def json(self):
        '''Returns a json representation of this blob.'''
        return json.dumps(self.serialized)

    @staticmethod
    def create_sentence_objects(blob):
        '''Returns a list of Sentence objects given
        a list of sentence strings. Attempts to handle sentences that
        have more than one puntuation mark at the end of the sentence.
        Examples: "An ellipses is no problem..." or "This is awesome!!!"
        '''
        sentence_objects = []
        sentences = sent_tokenize(blob)  # List of raw sentences
        # if there is only one sentence or string of text
        if len(sentences) <= 1:
            sentence_objects.append(Sentence(sentences[0], start_index=0,
                                    end_index=len(sentences[0]) - 1))
        else:
        # If there are many sentences
            char_index = 0  # Keeps track of character index within the blob
            for i, raw_sentence in enumerate(sentences):
                # Compute the start and end indices of the sentence
                # within the blob
                start_index = char_index
                char_index += len(raw_sentence)

                # Sometimes the NLTK tokenizer misses some punctuation when
                # there are multiple punctuations, e.g. with ellipses ("...")
                # or multiple exclamation points ("!!!")
                try:
                    next = sentences[i + 1]  # the next token
                except IndexError:
                    # Continue if the last token is a punctuation
                    if len(raw_sentence) <= 1:
                        continue
                    pass
                # If the next token is 1 character, assume it's a punctuation
                if len(next) == 1:
                    raw_sentence += next  # append the extra punctuation
                    char_index += 1  # also correct the char_index
                # Create a Sentence object and add it the the list
                sentence_objects.append(Sentence(raw_sentence,
                        start_index=start_index, end_index=char_index))
        return sentence_objects


class Sentence(BaseBlob):

    '''A sentence within a TextBlob.'''

    def __init__(self, sentence, start_index=0, end_index=None):
        '''Initialize a Sentence.

        Arguments:
        - sentence: A string, the raw sentence.
        - start_index: An int, the index where this sentence begins
                            in a TextBlob. If not given, defaults to 0.
        - end_index: An int, the index where this sentence ends in
                            a TextBlob. If not given, defaults to the
                            length of the sentence - 1.
        '''
        super(Sentence, self).__init__(sentence)
        self.start = self.start_index = start_index
        self.end = self.end_index = (end_index if end_index else len(sentence)
                                     - 1)

    @property
    def dict(self):
        '''The dict representation of this sentence.'''
        return {
            'raw': self.raw,
            'start_index': self.start_index,
            'end_index': self.end_index,
            'stripped': self.stripped,
            'noun_phrases': self.noun_phrases,
            'sentiment': self.sentiment,
            }
