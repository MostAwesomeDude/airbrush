# Copyright (C) 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
table = """
h                                                  he
li be                               b  c  n  o  f  ne
na mg                               al si p  s  cl ar
k  ca sc ti v  cr mn fe co ni cu zn ga ge as se br kr
rb sr y  zr nb mo tc ru rh pd ag cd in sn sb te i  xe
cs ba    hf ta w  re os ir pt au hg ti pb bi po at rn
fr ra    rf db sg bh hs mt ds rg cn    fl    lv

      la ce pr nd pm sm eu gd tb dy ho er tm yb lu
      ac th pa u  np pu am cm bk cf es fm md no lr
"""

elements = set([s.strip() for s in table.split()])

def match_word(w):
    """
    Return a list of lists of elements which concatenate to the given word.

    It is obviously possible for a word to have no matches.
    """

    if not w:
        return []

    partials = [(w, [])]
    finished = []

    while partials:
        part, l = partials.pop()

        if not part:
            finished.append(l)
        elif part[0] in elements:
            partials.append((part[1:], l + [part[0]]))
        if len(part) >= 2 and part[:2] in elements:
            partials.append((part[2:], l + [part[:2]]))

    return finished
