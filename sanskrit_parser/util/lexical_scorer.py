'''
Scorer for lexical splits

Uses word2vec based scoring the splits. The splits are
passed through sentencepiece first to handle possibly unseen words

Requires sentencepiece to be installed

@author: avinashvarna
'''

from __future__ import print_function, unicode_literals
import os
import sys
import six
import gensim
import logging
import requests
import sentencepiece as spm


class Scorer(object):

    # TODO - Install the data in a different way
    sentencepiece_file_url = "https://github.com/kmadathil/sanskrit_parser/blob/master/data/sentencepiece.model?raw=true"
    word2vec_file_url = "https://github.com/kmadathil/sanskrit_parser/blob/master/data/word2vec_model.dat?raw=true"
    base_dir = os.path.expanduser("~/.sanskrit_parser/data/")
    sentencepiece_file = os.path.join(base_dir, "sentencepiece.model")
    word2vec_file = os.path.join(base_dir, "word2vec_model.dat")

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._get_file(self.sentencepiece_file, self.sentencepiece_file_url)
        self._get_file(self.word2vec_file, self.word2vec_file_url)
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load(self.sentencepiece_file)
        self.model = gensim.models.Word2Vec.load(self.word2vec_file)

    def score_splits(self, splits):
        sentences = [" ".join(map(six.text_type, split)) for split in splits]
        return self.score_strings(sentences)

    def score_strings(self, sentences):
        self.logger.debug("Sentence = %s", sentences)
        pieces = [self.sp.EncodeAsPieces(sentence) for sentence in sentences]
        self.logger.debug("Pieces = %s", pieces)
        scores = self.model.score(pieces, total_sentences=len(sentences))
        self.logger.debug("Score = %s", scores)
        return scores

    def _get_file(self, local, url):
        if not os.path.exists(local):
            self.logger.debug("%s not found. Fetching from %s", local, url)
            r = requests.get(url, stream=True)
            with open(local, "wb") as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Lexical Scorer')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('data', nargs="?", type=six.text_type, default=None)

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    score = Scorer().score_strings([args.data])
    print("Input:", args.data)
    print("Score =", score)
