# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques vincent@vincent-jacques.net
# Copyright 2012 Zearin zearin@gonk.net
# Copyright 2013 Vincent Jacques vincent@vincent-jacques.net

# This file is part of PyGithub. http://jacquev6.github.com/PyGithub/

# PyGithub is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# PyGithub is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with PyGithub.  If not, see <http://www.gnu.org/licenses/>.


class InputGitAuthor(object):
    """
    """

    def __init__(self, name, email, date):
        """
        :param name: string
        :param email: string
        :param date: string
        """

        assert isinstance(name, (str, unicode)), name
        assert isinstance(email, (str, unicode)), email
        assert isinstance(date, (str, unicode)), date  # @todo Datetime?
        self.__name = name
        self.__email = email
        self.__date = date

    @property
    def _identity(self):
        return {
            "name": self.__name,
            "email": self.__email,
            "date": self.__date,
        }
