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
        self.s = s
        n = len(s)
        self.trigrams = [s[max(0, i):min(n, i+3)] for i in range(-2, n)]
        self.trigrams_length = len(self.trigrams)

    def score(self, s):
        n = len(s)
        union = 0
        for i in range(-2, n):
            x = s[max(0, i):min(n, i+3)]
            for c in self.trigrams:
                if c == x:
                    union += 1
        return 2 * union / (n + self.trigrams_length)
