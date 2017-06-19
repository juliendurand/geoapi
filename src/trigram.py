"""
Copyright (C) 2016 Julien Durand

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class Trigram():

    def __init__(self, s):
        # Construction of the list of trigrams of the string s.
        # First and last letter and couple of letters are included
        trigram_list = [s[max(0, i):min(len(s), i + 3)]
                        for i in range(-2, len(s))]

        # Object fields instantiation
        self.s = s
        self.trigrams = set(trigram_list)

    def score(self, s):
        """
        Computes the socre of similqrity between self.s and s

        Keyword arguments:
        s -- the string to compare
        """

        # Construction of the list of trigrams of the string s.
        # First and last letter and couple of letters are included.
        trigram_list = [s[max(0, i):min(len(s), i + 3)]
                        for i in range(-2, len(s))]

        intersection = set(trigram_list) & self.trigrams

        # Computation of the final score.
        return 2 * len(intersection) / (len(s) + len(self.s) + 4)
