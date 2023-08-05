# -*- coding: utf-8 -*-
# Stalker a Production Asset Management System
# Copyright (C) 2009-2013 Erkan Ozgur Yilmaz
# 
# This file is part of Stalker.
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import os
import logging

from stalker import Version

logger = logging.getLogger(__name__)


class EnvironmentBase(object):
    """Connects the environment (the host program) to Stalker.

    In Stalker, an Environment is a host application like Maya, Nuke, Houdini
    etc.

    Generally a GUI for the end user is given an environment which helps the
    QtGui to be able to open, save, import or export a Version without
    knowing the details of the environment.

    To create a new environment for you own program, just instantiate this
    class and override the methods as necessary. And call the UI with by giving
    an environment instance to it, so the interface can call the correct
    methods as needed.

    Here is an example how to create an environment for a program and use the
    GUI::

        from Stalker import EnvironmentBase

        class MyProgramEnv(EnvironmentBase):
            \"""This is a class which will be used by the UI
            \"""

            def open():
                \"""uses the programs own Python API to open a version of an
                asset
                \"""

                # do anything that needs to be done before opening the file
                my_programs_own_python_api.open(filepath=self.version.full_path)

            def save():
                \"""uses the programs own Python API to save the current file
                as a new version.
                \"""

                # do anything that needs to be done before saving the file
                my_programs_own_python_api.save(filepath=self.version.full_path)

                # do anything that needs to be done after saving the file

    and that is it.

    The environment class by default has a property called ``version``.
    Holding the current open version. It is None for a new scene and a
    :class:`~stalker.models.version.Version` instance in any other
    case.

    :param name: To initialize the class the name of the environment should be
        given in the name argument. It can not be skipped or None or an empty
        string.
    """

    name = "EnvironmentBase"

#    def __init__(self, name=""):
#        self._name = name
#        self._extensions = []
#        self._version = None

    def __str__(self):
        """the string representation of the environment
        """
        return self._name
    
    @property
    def version(self):
        """returns the current Version instance which is open in the
        environment
        """
        return self.get_current_version()

    @property
    def name(self):
        """returns the environment name
        """
        return self._name

    @name.setter
    def name(self, name):
        """sets the environment name
        """
        self._name = name

    def save_as(self, version):
        """The save as action of this environment. It should save the current
        scene or file to the given version.full_path
        """
        raise NotImplementedError

    def export_as(self, version):
        """Exports the contents of the open document as the given version.

        :param version: A :class:`~stalker.models.version.Version` instance
          holding the desired version.
        """
        raise NotImplementedError

    def open_(self, version, force=False):
        """the open action
        """
        raise NotImplementedError

    def post_open(self, version):
        """Runs after opening a file
        """
        raise NotImplementedError

    def import_(self, asset):
        """the import action
        """
        raise NotImplementedError

    def reference(self, asset):
        """the reference action
        """
        raise NotImplementedError
    
    def trim_server_path(self, path_in):
        """Trims the server_path value from the given path_in

        :param path_in: The path that wanted to be trimmed
        :return: str
        """
        server_path = os.environ['REPO'].replace('\\', '/')
        if path_in.startswith(server_path):
            length = len(server_path)
            if not server_path.endswith('/'):
                length += 1
            path_in = path_in[length:]
        return path_in
    
    def get_versions_from_path(self, path):
        """Finds Version instances from the given path value.

        Finds and returns the :class:`~stalker.models.version.Version`
        instances from the given path value.

        Returns an empty list if it can't find any matching.

        This method is different than
        :meth:`~stalker.env.EnvironmentBase.get_version_from_full_path`
        because it returns a list of
        :class:`~oyProjectManager.models.version.Version` instances which are
        residing in that path. The list is ordered by the ``id``\ s of the
        instances.

        :param path: A path which has possible
            :class:`~oyProjectManager.models.version.Version` instances.

        :return: A list of :class:`~satlker.models.version.Version` instances.
        """
        if path is None or path=="":
            return None

        # get the path by trimming the server_path
        path = path.replace('\\', '/')
        path = self.trim_server_path(path)

        # get all the version instance at that path
        return Version.query\
            .filter(Version.path.startswith(path))\
            .order_by(Version.id.desc())\
            .all()

    def get_version_from_full_path(self, full_path):
        """Finds the Version instance from the given full_path value.

        Finds and returns a :class:`~stalker.models.version.Version` instance
        from the given full_path value.

        Returns None if it can't find any matching.

        :param full_path: The full_path of the desired
            :class:`~stalker.models.version.Version` instance.

        :return: :class:`~stalker.models.version.Version`
        """

        path, filename = os.path.split(full_path)
        path = self.trim_server_path(path)

        logger.debug('path: %s' % path)

        # try to get a version with that info
        version = Version.query()\
            .filter(Version.path==path)\
            .filter(Version.filename==filename)\
            .first()

        return version
    
    def get_current_version(self):
        """Returns the current Version instance from the environment.

        :returns: :class:`~stalker.models.version.Version` instance or None
        """
        raise NotImplementedError

    def get_last_version(self):
        """Returns the last opened Version instance from the environment.

        * It first looks at the current open file full path and tries to match
          it with a Version instance.
        * Then searches for the recent files list.
        * Still not able to find any Version instances, will return the version
          instance with the highest id which has the current workspace path in
          its path
        * Still not able to find any Version instances returns None

        :returns: :class:`~stalker.models.version.Version` instance or None.
        """
        raise NotImplementedError

    def get_project(self):
        """returns the current project from environment
        """
        raise NotImplementedError

    def set_project(self, version):
        """Sets the project to the given Versions project.

        :param version: A :class:`~stalker.models.version.Version`.
        """
        raise NotImplementedError

#    def setOutputFileName(self):
#    def set_output_path(self):
#        """sets the output file names
#        """
#        raise NotImplementedError

#    def append_to_recent_files(self, path):
#        """appends the given path to the recent files list
#        """
#        raise NotImplementedError

    def check_referenced_versions(self):
        """Checks the referenced versions

        :returns: list of Versions
        """
        raise NotImplementedError

    def get_referenced_versions(self):
        """Returns the :class:`~stalker.models.version.Version` instances which
        are referenced in to the current scene

        :returns: list of :class:`~stalker.models.version.Version` instances.
        """
        raise NotImplementedError

#    def update_versions(self, version_tuple_list):
#        """updates the assets to the latest versions
#        """
#        raise NotImplementedError

    def get_frame_range(self):
        """Returns the frame range from the environment

        :returns: a tuple of integers containing the start and end frame
            numbers
        """
        raise NotImplementedError

    def set_frame_range(self, start_frame=1, end_frame=100,
                        adjust_frame_range=False):
        """Sets the frame range in the environment to the given start and end
        frames
        """
        raise NotImplementedError

    def get_fps(self):
        """Returns the frame rate of this current environment
        """
        raise NotImplementedError

    def set_fps(self, fps=25):
        """Sets the frame rate of the environment. The default value is 25.
        """
        raise NotImplementedError

    @property
    def extensions(self):
        """Returns the valid native extensions for this environment.

        :returns: a list of strings
        """
        return self._extensions

    @extensions.setter
    def extensions(self, extensions):
        """Sets the valid native extensions of this environment.

        :param extensions: A list of strings holding the extensions. Ex:
            ["ma", "mb"] for Maya
        """
        self._extensions = extensions

    def has_extension(self, filename):
        """Returns True if the given file names extension is in the extensions
        list false otherwise.

        accepts:
        * a full path with extension or not
        * a file name with extension or not
        * an extension with a dot on the start or not

        :param filename: A string containing the filename
        """
        if filename is None:
            return False
        return filename.split('.')[-1].lower() in self.extensions

    def load_referenced_versions(self):
        """loads all the references
        """
        raise NotImplementedError

    def replace_version(self, source_version, target_version):
        """Replaces the source_version with the target_version

        :param source_version: A
          :class:`~stalker.models.version.Version` instance holding the version
          to be replaced

        :param target_version: A
          :class:`~stalker.models.version.Version` instance holding the new
          version replacing the source one.
        """
        raise NotImplementedError

    def replace_external_paths(self, mode=0):
        """Replaces the external paths (which are not starting with the
        environment variable) with a proper path. The mode controls if the
        resultant path should be absolute or relative to the project dir.

        :param mode: Controls the resultant path is absolute or relative.

          mode 0: absolute (a path which starts with $REPO)
          mode 1: relative (to project path)

        :return:
        """
        raise NotImplementedError

