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
        self.trigrams = [s[i:i+3] for i in range(0, len(s)-2)]
        self.trigrams_length = len(self.trigrams)

    def score(self, s):
        n = len(s)-2
        union = 0
        for i in range(0, n):
            x = s[i:i+3]
            for c in self.trigrams:
                if c == x:
                    union += 1
        return 2 * union / (n + self.trigrams_length)


if __name__ == '__main__':
    t = Trigram('rue de la connardiere')
    print(t.score('chemin de la cognardiere'))
