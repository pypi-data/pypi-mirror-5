# -*- coding: utf-8 -*-

"""Module containing worker functionality for the MDP implementation.

For the MDP specification see: http://rfc.zeromq.org/spec:7
"""

__license__ = """
    This file is part of MDP.

    MDP is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MDP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MDP.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'shykes (Solomon Hykes)'
__email__ = 'solomon.hykes@gmail.com'


from setuptools import setup

setup(
    name        = 'pyzmq-mdp',
    version     = '0.2',
    description = 'ZeroMQ MDP protocol in Python using pyzmq',
    author      = 'Guido Goldstein',
    author_email= 'gst-py@a-nugget.de',
    url         = 'https://github.com/guidog/pyzmq-mdp',
    package_dir = {'mdp': 'mdp'},
    packages    = ['mdp'],
    zip_safe    = False,
    use_2to3    = True
)
