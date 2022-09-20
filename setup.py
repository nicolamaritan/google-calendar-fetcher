# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='google-calendar-fetcher',
    version="1.0",
    packages=find_packages(),
    author="nicolamaritan",
    url='https://github.com/nicolamaritan/google_calendar_fetcher/',
    entry_points = {'console_scripts': ['gcfetch = google_calendar_fetcher.core:main']},
    install_requires=["google",
                      "google_auth_oauthlib",
                      #"googleapiclient",
                      "pytz",
                      "colorama",
                      ],
    classifiers=[
        "Programming Language :: Python",
    ],
)