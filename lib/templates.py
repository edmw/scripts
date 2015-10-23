# coding: utf-8

from wheezy import template as wheezy
from wheezy.html.utils import escape_html

from bs4 import BeautifulSoup
from tidylib import tidy_document

class TemplateEngine:
    def __init__(self, template_path):
        self.template_path = template_path

        self.template_engine = wheezy.engine.Engine(
            loader=wheezy.loader.FileLoader([self.template_path]),
            extensions=[wheezy.ext.core.CoreExtension()]
        )
        self.template_engine.global_vars.update({'e': escape_html})

        self.templates = {}

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

