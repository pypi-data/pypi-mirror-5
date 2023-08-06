# This file is part of python-markups test suite
# License: BSD
# Copyright: (C) Dmitry Shachnev, 2012

import unittest
from markups import ReStructuredTextMarkup

basic_text = \
'''Hello, world!
=============

This is an example **reStructuredText** document.'''

class ReStructuredTextTest(unittest.TestCase):
	def test_basic(self):
		markup = ReStructuredTextMarkup()
		text = markup.get_document_body(basic_text)
		title = markup.get_document_title(basic_text)
		markup.enable_cache = True
		text_from_cache = markup.get_document_body(basic_text)
		title_from_cache = markup.get_document_title(basic_text)
		text_expected = \
		'<p>This is an example <strong>reStructuredText</strong> document.</p>\n'
		title_expected = 'Hello, world!'
		self.assertEqual(text_expected, text)
		self.assertEqual(text_expected, text_from_cache)
		self.assertEqual(title_expected, title)
		self.assertEqual(title_expected, title_from_cache)
	
	def test_mathjax_loading(self):
		markup = ReStructuredTextMarkup()
		self.assertEqual('', markup.get_javascript('Hello, world!'))
		js = markup.get_javascript('Hello, :math:`2+2`!')
		self.assertIn('<script', js)
		body = markup.get_document_body('Hello, :math:`2+2`!')
		self.assertIn('<span class="math">', body)
		self.assertIn(r'\(2+2\)</span>', body)

if __name__ == '__main__':
	unittest.main()
