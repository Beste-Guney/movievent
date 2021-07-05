"""
Strict count vectorizer.

"""
from sklearn.feature_extraction.text import CountVectorizer

from sklearn_text_extensions.ngrams import iter_ngrams


class StrictCountVectorizer(CountVectorizer):
    """
    Modifies the default sklearn CountVectorizer to behave in a more predictable way.

    Notably:

    * Stop word extraction happens logically after creating ngrams (See inline docstring below)

    """
    def _word_ngrams(self, tokens, stop_words=None):
        """
        This is a modification to the original sklearn CountVectorizer tokenization.

        In their implementation, stop words are extracted first and then ngrams are generated.
        This leads to creation of artificial ngrams, for example the text 'partner who can develop',
        may be reduced to 'partner develop' after removing stop words, which would result in 'partner develop'
        being extracted as an ngram.

        We modify this logic instead to generate all ngrams first, and then remove ones which are either:

        * unigrams corresponding to items in the stop_words list
        * ngrams which are comprised *exclusively* of stop words.

        See original for reference:
        https://github.com/scikit-learn/scikit-learn/blob/a24c8b46/sklearn/feature_extraction/text.py#L541

        """
        ngrams = iter_ngrams(
            list(tokens),
            ngram_range=self.ngram_range,
        )

        if stop_words is not None:
            ngrams = (
                ngram
                for ngram in ngrams
                if set(ngram).difference(stop_words)
            )

        return [
            " ".join(ngram)
            for ngram in ngrams
        ]
