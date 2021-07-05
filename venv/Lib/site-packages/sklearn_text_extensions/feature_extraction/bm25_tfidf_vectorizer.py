import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class BM25TfidfVectorizer(TfidfVectorizer):
    """
    Extended sklearn TfidfVectorizer to use BM25 TfIdf variant.

    Parameters
    ----------
    Same set of parameters as in
    http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
    with additional/updated parameters:

    k : float, default=1.2
        BM25 parameter k
    b : float, default=0.75
        BM25 parameter b
    use_idf : bool
        This will be ignored, disregarding input.
    norm : str
        This will be ignored, disregarding input.

    """

    def __init__(self, **kwargs):
        kwargs["use_idf"] = True
        kwargs["norm"] = None

        self.bm25_k_ = kwargs.pop("k") if "k" in kwargs else 1.2
        self.bm25_b_ = kwargs.pop("b") if "b" in kwargs else 0.75

        super(BM25TfidfVectorizer, self).__init__(**kwargs)

    def fit_transform(self, documents, y=None, weight_scheme='bm25', norm='l2'):
        """
        Fit transform documents with options to use BM25.

        Parameters
        ----------
        documents : list
            An array of strings
        weight_scheme : string {'bm25'|'tfidf'}
            Weight scheme to use for return vectors
        norm : string {'l2'|'l1'|None}
            Normalization of return vectors

        Returns
        ------
        scipy.sparse.csr_matrix of shape (num_documents, len(self.vocabulary_))

        """
        vecs = super(BM25TfidfVectorizer, self).fit_transform(documents)
        self.idf_arr_ = self.idf_.copy()
        # Requires the setter decorator
        self.use_idf = False

        # convert vecs to original tf and compute the median/avg doc length
        df_arr_sparse = csr_matrix(1 / self.idf_arr_)
        self.idf_arr_ = csr_matrix(self.idf_arr_)
        vecs = vecs.multiply(df_arr_sparse)
        lengths = np.array(vecs.sum(axis=1).T)[0]
        self.median_length_ = np.median(lengths)
        self.average_length_ = np.average(lengths)

        return self.transform_tfs(
            tfs=vecs,
            weight_scheme=weight_scheme,
            norm=norm,
        )

    def transform(self, documents, weight_scheme='bm25', norm='l2'):
        """
        Transform documents with options to use BM25.

        Parameters
        ----------
        documents : list
            An array of strings
        weight_scheme : string {'bm25'|'tfidf'}
            Weight scheme to use for return vectors
        norm : string {'l2'|'l1'|None}
            Normalization of return vectors

        Returns
        ------
        scipy.sparse.csr_matrix of shape (num_documents, len(self.vocabulary_))

        """
        tfs = super(BM25TfidfVectorizer, self).transform(documents)

        return self.transform_tfs(
            tfs=tfs,
            weight_scheme=weight_scheme,
            norm=norm
        )

    def transform_tfs(self, tfs, weight_scheme='bm25', norm='l2'):
        k = self.bm25_k_
        b = self.bm25_b_
        idf = self.idf_arr_
        avg_doc_length = self.average_length_

        if weight_scheme == 'bm25':
            d_arr = np.array(tfs.sum(axis=1).T)[0]
            tfs_coo = tfs.tocoo()
            tfs_data, row, col = tfs_coo.data, tfs_coo.row, tfs_coo.col
            # https://en.wikipedia.org/wiki/Okapi_BM25
            # sparse element-wise operation
            bm25_tfs = ((k + 1) * tfs_data) / (k * (1.0 - b + b * (d_arr[row] / avg_doc_length)) + tfs_data)
            # construct the sparse matrix again
            bm25_tfs = csr_matrix((bm25_tfs, (row, col)), shape=tfs.shape)
            vecs = idf.multiply(bm25_tfs)
        else:
            vecs = idf.multiply(tfs)

        if norm is not None:
            return normalize(vecs, norm=norm, copy=False)
        else:
            return vecs

    @property
    def idf_(self):
        return self._tfidf.idf_

    @property
    def use_idf(self):
        return self._tfidf.use_idf

    @use_idf.setter
    def use_idf(self, value):
        self._tfidf.use_idf = value
