# coding: utf-8

import re

from wheezy import template as wheezy
from wheezy.html.utils import escape_html

from bs4 import BeautifulSoup
from tidylib import tidy_document

from json import dumps as encode_json

import pyphen

class TemplateEngine:
    def __init__(self, template_path):
        self.pyphen_dictionary = pyphen.Pyphen(lang='de_DE')

        self.template_path = template_path

        self.template_engine = wheezy.engine.Engine(
            loader=wheezy.loader.FileLoader([self.template_path]),
            extensions=[wheezy.ext.core.CoreExtension()]
        )
        self.template_engine.global_vars.update({'e': escape_html})
        self.template_engine.global_vars.update({'j': encode_json})
        self.template_engine.global_vars.update({'h': self.hyphenate})

        self.templates = {}

    def hyphenate_word(self, word, hyphen='\u00ad'):
      if self.pyphen_dictionary:
          word_len = len(word)
          word_list = list(word)
          # iterate over possible hyphen positions
          for position in reversed(self.pyphen_dictionary.positions(word)):
              if position.data:
                  change, index, cut = position.data
                  index += position
                  if word.isupper():
                      change = change.upper()
                  word_list[index:index + cut] = change.replace('=', hyphen)
              else:
                  # insert hyphen if length of syllable is greater than 2
                  if position > 2 and position < (word_len - 2):
                      word_list.insert(position, hyphen)
          return ''.join(word_list)
      else:
          return word

    def hyphenate(self, text, hyphen='\u00ad'):
        # split string into words, punctation and whitespace
        components = re.findall(r"\w+|[^\w]", text, re.UNICODE)
        # insert soft hyphens for words
        # (punctation and whitespace will be ignored)
        components = [self.hyphenate_word(element, hyphen) for element in components]
        # join string again
        return ''.join(components)

    def pretty(self, html):
        soup = BeautifulSoup(html, "html5lib")
        document, errors = tidy_document(soup.encode(formatter="html"), options={
            'char-encoding': 'utf8',
            'output-encoding': 'utf8',
            'doctype': 'html5'
        })
        return document

    def render(self, template_name, value_dict):
        template = self.templates.get(template_name)
        if not template:
            template = self.template_engine.get_template(template_name)
            self.templates[template_name] = template
        return self.pretty(template.render(value_dict))

