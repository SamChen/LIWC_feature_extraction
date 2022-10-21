#!/usr/bin/env python

import re
import numpy as np
import sys
import warnings
from collections import defaultdict
import pandas as pd

import tri_search

class LIWC_feature_extract:
    def __init__(self, map_table, scale=True, get_n_total=True, get_n_oov=True):
        self.liwc_dict_root = self._load_LIWC(map_table)
        self.scale = scale
        self.get_n_total = get_n_total
        self.get_n_oov = get_n_oov

    def _load_LIWC(self, map_table):
        liwc_mode = -1
        root = tri_search.Node("ROOT")
        self.liwc_maps = {}
        self.liwc_wild = {}
        self.liwc_key2cat = {}

        with open(map_table,'r') as liwc_file:
            for line in liwc_file:
                line = line.strip()
                #pdb.set_trace()
                if re.match(r'^%.*',line):
                    liwc_mode += 1
                elif liwc_mode == 0:
                    keyid, cat = line.split()
                    self.liwc_key2cat[keyid] = cat
                else:
                    word, *keyids = line.split()
                    try:
                        tri_search.insert(root, word,[self.liwc_key2cat[v] for v in keyids])
                    except BaseException:
                        # https://github.com/USC-CSSL/TACIT/issues/472 There are two entries that I did not find standard process for them.
                        warnings.warn("unusual input: {}".format(line), UserWarning)

        return root


    def fit(self, X, y):
        return self

    def transform(self, X):
        return np.array([ self._extractor(words).values() for words in X ])


    def _check_liwc_wild(self, word):
        '''
        return T/F and save result in self.last_succ_search
        '''

        for wild in self.liwc_wild.keys():
            if re.search("^"+wild, word):
                self.last_succ_wild_search = {word: self.liwc_wild[wild]}
                return True

        return False

    def _extractor(self, pt_transcript):
        '''
        input pt_transcript should either be a list or a generator
        '''
        assert isinstance(pt_transcript, str)
        oov_cnt = 0
        total_cnt=0
        liwc_count={f"liwc_{cat}":0 for cat in self.liwc_key2cat.values()}

        for word in pt_transcript.split():
            # words = line.strip().split()

            # for word in words:
            if re.match("^\d+$", word):
                print(word)
            total_cnt += 1
            temp = tri_search.find(self.liwc_dict_root, word)
            if temp:
                for cat in temp:
                    liwc_count[f"liwc_{cat}"] += 1
            else:
                oov_cnt += 1

        # features = list(liwc_count.values()) + [ total_cnt , miss_cnt ]
        assert list(liwc_count.values()) == [cnt for cnt in liwc_count.values()]
        features = liwc_count
        if self.get_n_total:
            features["liwc_total_cnt"] = total_cnt
        if self.get_n_oov:
            features["liwc_oov_cnt"] = oov_cnt

        if self.scale:
            denominator = total_cnt + 1e-16
            for key in features:
                if key in ["liwc_total_cnt"]:
                    continue
                features[key] = features[key] / denominator


        return features

    def get_features(self, df):
        assert isinstance(df, pd.DataFrame)
        outputs = defaultdict(list)
        # for ptid, text in zip(data["subjects"], data["text"]):
        for _, row in df.iterrows():
            ptid = row.ptid
            text = row.text
            outputs["subjects"].append(ptid)

            features = self._extractor(text)
            for key in features:
                outputs[key].append(features[key])

        outputs = pd.DataFrame.from_dict(outputs)
        return outputs
