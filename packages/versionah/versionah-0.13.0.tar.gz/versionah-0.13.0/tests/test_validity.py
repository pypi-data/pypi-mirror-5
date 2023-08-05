#! /usr/bin/python -tt
# coding=utf-8
"""test_validity - Version validity tests"""
# Copyright © 2011, 2012, 2013  James Rowe <jnrowe@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from expecter import expect
from nose2.tools import params

from versionah import Version


@params(
    '1',
    '1.2.3.4.5',
    '1.2.-1.0',
)
def test_version_validation(v):
    with expect.raises(ValueError, 'Invalid version string %r' % v):
        Version(v)
