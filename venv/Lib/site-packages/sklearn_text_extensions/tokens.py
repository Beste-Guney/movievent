"""
Tokenization helpers.

"""
import re
from functools import partial


def identity(x):
    return x


def split_spaces(string):
    """
    Baseline string splitter which will split text into tokens
    on whitespaces.

    """
    return string.split()


def split_punctuation(string, punctuation):
    regexp = r"[\w]+|[" + re.escape(punctuation) + "]"
    return re.findall(regexp, string)


def modular_tokenize(
    text,
    splitter=None,
    punctuation=None,
    stop_words=None,
    stemmer=identity,
    translate_table=None,
):
    """
    Modular tokenizer wrapper with pluggable base tokenizer, punctuation, stop words, and stemmer.

    In particular, meant to be used in conjunction with sklearn-compatible vectorizers and retain
    serializability, e.g. via `joblib.dump`.

    Can be used with `functools.partial` to set the configurable parts once and then use on
    variable text, e.g:

    >>> tokenize = partial(modular_tokenize, stop_words=STOP_WORDS)
    >>> tokenize("my text")
    ["my"]

    :param text: {str} the text to tokenize
    :param splitter: {callable} a callable to use to split string into tokens
    :param punctuation: {iterable} a sequence of punctuation characters. If provided,
        and no custom splitter is given, tokenizer will by default split on punctuation
        characters as well as whitespaces.
    :param stop_words: {iterable} a sequence of stop words. If provided, these will be
        filtered out from emitted tokens. Note that if it is of interest to retain stop words
        as part of extracting ngrams (bigrams, trigrams), you should not generally perform
        the filtering here. See also `sklearn_text_extensions.feature_extraction.StrictCountVectorizer`
    :param stemmer: {callable} (optional) stemmer that will be applied to each token emitted
    :param translate_table: {iterable} (optional) table of character that will be used to
        translate certain characters on given text using Python's `string.translate()`.
    :returns generator expression yielding the tokens

    """
    if translate_table:
        text = text.translate(translate_table)
    if not stemmer:
        stemmer = identity
    if not stop_words:
        stop_words = set()
    if not punctuation:
        punctuation = set()
    if punctuation and not splitter:
        # We have a punctuation list and no custom splitter defined,
        # use our default punctuation-aware splitter
        splitter = partial(split_punctuation, punctuation=punctuation)
    elif not splitter:
        # No punctuation and no custom splitter defined
        splitter = split_spaces

    yield from (
        stemmer(token)
        for token in splitter(text.strip())
        if not (
            token in punctuation or
            token in stop_words
        )
    )
