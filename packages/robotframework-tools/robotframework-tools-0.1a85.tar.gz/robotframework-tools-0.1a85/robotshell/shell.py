# robotframework-tools
#
# Tools for Robot Framework and Test Libraries.
#
# Copyright (C) 2013 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# robotframework-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# robotframework-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with robotframework-tools. If not, see <http://www.gnu.org/licenses/>.

"""robotshell.shell

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['RobotPlugin']

import re
import os
from itertools import chain

from robottools import TestRobot
from robottools.testrobot import Keyword

from .base import ShellBase
from .magic import (
  RobotMagics, RobotMagic, KeywordMagic, KeywordCellMagic, VariableMagic)

from .extension import ExtensionMagic

class RobotShell(ShellBase):
    # To support customization in derived Plugins
    robot_magic_name = 'Robot'

    robot_debug_mode = False
    robot_cell_magic_mode = False

    def __init__(self, shell, default_robot_name='Default'):
        ShellBase.__init__(self, shell)
        self.label = None

        for name, value in os.environ.items():
            self.line_magics['{%s}' % name] = (
              lambda _, _value=value: _value)

        self.line_magics[self.robot_magic_name] = RobotMagic(
          robot_shell=self)

        magics = RobotMagics(robot_shell=self)
        shell.register_magics(magics)

        self.robot = None
        self.robots = {}
        self.robot_keyword_magics = {}
        self.robot_keyword_cell_magics = {}
        self.robot_variable_magics = {}

        # Create initial default Test Robot
        self.Robot(default_robot_name)

    def Robot(self, name=None, extname=None):
        if name and (not self.robot or name != self.robot.name):
            try:
                robot = self.robots[name]
            except KeyError:
                robot = TestRobot(name)
                self.robots[name] = robot
            self.robot = robot

            robot_magic = RobotMagic(name, robot_shell=self)
            self.line_magics[str(robot_magic)] = robot_magic

            self.unregister_robot_magics()
            self.register_robot_variable_magics()
            for alias, lib in robot._libraries.items():
                self.register_robot_keyword_magics(alias, lib)

        try:
            label = self.robot.magic_name
        except AttributeError:
            label = '%s.%s' % (self.robot_magic_name, name)
        else:
            if extname:
                label += '.' + extname
        self.in_template = re.sub(
          r'^(\[%s\]\n)?' % self.label, '[%s]\n' % label, self.in_template)
        self.label = label

        return self.robot

    def Import(self, libname, alias=None):
        library = self.robot.Import(libname, alias)
        self.register_robot_keyword_magics(alias or libname, library)
        return library

    def register_robot_keyword_magics(self, libalias, library):
        for keyword in library:
            keywordname = keyword.name.replace(' ', '')
            for name in keywordname, '%s.%s' % (libalias, keywordname):
                keyword = Keyword(keyword._handler, self.robot._context)

                keyword_magic = KeywordMagic(keyword, robot_shell=self)
                self.robot_keyword_magics[name] = keyword_magic

                self.line_magics[name] = keyword_magic

                ## keyword_cell_magic = KeywordCellMagic(
                ##   keyword, robot_shell=self)
                ## self.robot_keyword_cell_magics[name] = keyword_cell_magic

                ## cell_magics[name] = keyword_cell_magic

    def register_robot_variable_magics(self):
        for var in self.robot._variables:
            for name in [var, var + '=']:
                magic = VariableMagic(var, robot_shell=self)
                self.robot_variable_magics[name] = magic
                self.line_magics[name] = magic

    def unregister_robot_magics(self):
        magics = self.line_magics
        for name in chain(
          self.robot_keyword_magics,
          self.robot_variable_magics
          ):
            del magics[name]
        self.robot_keyword_magics = {}
        self.robot_variable_magics = {}

        magics = self.cell_magics
        for name in self.robot_keyword_cell_magics:
            del magics[name]
        self.robot_keyword_cell_magics = {}

    def register_extension(self, extcls):
        extrobot = extcls()
        name = extrobot.magic_name
        self.robots[name] = extrobot
        self.Robot(name)

        ext_magic = ExtensionMagic(extrobot, robot_shell=self)
        self.line_magics[str(ext_magic)] = ext_magic
