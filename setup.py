# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='google-calendar-fetcher',
    version="1.0.7",
    packages=find_packages(),
    author="nicolamaritan",
    description="Command Line tool to quickly get Google Calendar events.",
    url='https://github.com/nicolamaritan/google_calendar_fetcher/',
    entry_points = {'console_scripts': ['gcf = google_calendar_fetcher.core:main']},
    install_requires=["google",
                      "google_auth_oauthlib",
                      "pytz",
                      "colorama",
                      ],
    classifiers=[
        "Programming Language :: Python",
    ],
)