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
from unittest import TestCase

from airbrush.elements import match_word

class TestMatchWord(TestCase):

    def test_no_matches(self):
        self.assertEqual([], match_word("jazz"))

    def test_single_match(self):
        self.assertEqual([["i", "v", "y"]], match_word("ivy"))

    def test_multiple_matches(self):
        self.assertEqual([['no', 'se'], ['n', 'o', 'se']], match_word("nose"))
