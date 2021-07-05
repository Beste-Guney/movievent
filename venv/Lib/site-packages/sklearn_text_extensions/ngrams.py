"""
Ngram extraction utilities.

"""


def iter_ngrams(tokens,  ngram_range=(1, 2)):
    """
    Return a generator expression yielding ngrams of span defined by the
    ngram_range parameter from the token stream provided.

    Note that for all cases, including unigrams, we yield lists.

    Examples:

    >>> list(iter_ngrams(["my", "tokenized", "text"], ngram_range=(1, 1)))
    [["my"], ["tokenized"], ["text"]]

    >>> list(iter_ngrams(["my", "tokenized", "text"], ngram_range=(1, 2)))
    [["my"], ["tokenized"], ["text"], ["my", "tokenized"], ["tokenized", "text"]]


    """
    # Nb. this implementation is mostly copied over from the original sklearn count vectorizer one.
    min_n, max_n = ngram_range

    if max_n == 1:
        # Only yield unigrams
        for unigram in tokens:
            yield [unigram]
        return

    original_tokens = tokens
    if min_n == 1:
        # no need to do any slicing for unigrams
        # just iterate through the original tokens
        for unigram in original_tokens:
            yield [unigram]
        min_n += 1

    n_original_tokens = len(original_tokens)

    for n in range(min_n, min(max_n + 1, n_original_tokens + 1)):
        for i in range(n_original_tokens - n + 1):
            yield original_tokens[i:i + n]
