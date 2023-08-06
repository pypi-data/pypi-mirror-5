#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "django-jinja",
    version = "0.17",
    description = "Jinja2 templating language integrated in Django.",
    long_description = "",
    keywords = "django, jinja2",
    author = "Andrey Antukh",
    author_email = "niwi@niwi.be",
    url = "https://github.com/niwibe/django-jinja",
    license = "BSD",
    packages = [
        "django_jinja",
        "django_jinja.builtins",
        "django_jinja.management",
        "django_jinja.management.commands",
        "django_jinja.contrib",
        "django_jinja.contrib.pipeline",
        "django_jinja.contrib.pipeline.templatetags",
        "django_jinja.contrib.easy_thumbnails",
        "django_jinja.contrib.easy_thumbnails.templatetags",
        "django_jinja.contrib.humanize",
        "django_jinja.contrib.humanize.templatetags",
    ],

    requires = [
        "jinja2 (>=2.5)",
        "django (>=1.4)",
    ],

    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Internet :: WWW/HTTP",
    ]
)
