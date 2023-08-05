# Generic modularized configuration file manager.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: July 6, 2013
# URL: https://pypi.python.org/pypi/update-dotdee

"""
Usage: update-dotdee FILENAME

Generate a (configuration) file based on the contents of the files in the
directory with the same name as FILENAME but ending in '.d'.

If FILENAME exists but the corresponding directory does not exist yet, the
directory is created and FILENAME is moved into the directory so that its
existing contents are preserved.
"""

# Standard library modules.
import getopt
import hashlib
import logging
import os
import os.path
import shutil
import sys
import textwrap

# External dependencies.
from coloredlogs import ColoredStreamHandler
from humanfriendly import format_path
from natsort import natsort

def main():
    """
    Command line interface for the ``update-dotdee`` program.
    """
    program = UpdateDotDee()
    try:
        if program.parse_arguments(sys.argv[1:]):
            program.update_file()
    except Exception, e:
        program.logger.exception(e)
        sys.exit(1)

class UpdateDotDee:

    """
    The update-dotdee program is implemented as a class which
    can be used both from the command line and as a Python API.
    """

    def __init__(self, filename=None, force=False):
        """
        Initialize the update-dotdee program.
        """
        self.force = force
        self.filename = filename
        self.initialize_logging()

    def initialize_logging(self):
        """
        Initialize the logging subsystem.
        """
        self.logger = logging.getLogger('update-dotdee')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(ColoredStreamHandler())

    def parse_arguments(self, arguments):
        """
        Parse and validate the command line arguments.
        """
        try:
            options, arguments = getopt.getopt(arguments, 'fvh', ['force', 'verbose', 'help'])
            for option, value in options:
                if option in ('-f', '--force'):
                    self.force = True
                elif option in ('-v', '--verbose'):
                    self.logger.setLevel(logging.DEBUG)
                elif option in ('-h', '--help'):
                    self.print_usage()
                    return False
                else:
                    # Programming error...
                    assert False, "Unhandled option!"
            if not arguments:
                self.print_usage()
                return False
            elif len(arguments) != 1:
                raise Exception, "Expected a filename as the first and only argument!"
            elif not os.path.isfile(arguments[0]):
                raise Exception, "The given filename doesn't point to an existing file!"
            self.filename = arguments[0]
            return True
        except Exception, e:
            self.logger.error("Failed to parse command line arguments!")
            self.logger.exception(e)
            self.print_usage()
            sys.exit(1)

    def print_usage(self):
        """
        Print a usage message to the console.
        """
        print textwrap.dedent(__doc__).strip()

    def update_file(self, force=None):
        """
        Update the file with the contents of the files in the ``.d`` directory.
        """
        if force is None:
            force = self.force
        if not os.path.isdir(self.directory):
            # Create the .d directory.
            self.logger.info("Creating directory %s", format_path(self.directory))
            os.makedirs(self.directory)
            # Move the original file into the .d directory.
            local_file = os.path.join(self.directory, 'local')
            self.logger.info("Moving %s to %s", format_path(self.filename), format_path(local_file))
            shutil.move(self.filename, local_file)
        # Read the modularized configuration file(s).
        blocks = []
        for filename in natsort(os.listdir(self.directory)):
            if not filename.startswith('.'):
                blocks.append(self.read_file(os.path.join(self.directory, filename)))
        contents = "\n\n".join(blocks)
        # Make sure the generated file was not modified?
        self.logger.info("Checking for local changes to %s", format_path(self.filename))
        current_checksum = self.hash_contents()
        if os.path.isfile(self.checksum_file):
            # Recall the previous checksum.
            handle = open(self.checksum_file)
            previous_checksum = handle.read()
            handle.close()
            # Compare the checksums.
            if current_checksum != previous_checksum:
                if force:
                    self.logger.warn("Contents of generated file were modified but --force was used.")
                else:
                    raise RefuseToOverwrite, "Contents of generated file were modified! Refusing to overwrite."
        # Update the generated file and the checksum.
        self.write_file(self.filename, contents)
        # Update the checksum.
        handle = open(self.checksum_file, 'w')
        handle.write(self.hash_contents())
        handle.close()

    def read_file(self, filename):
        """
        Read a text file and optionally provide feedback to the user.
        """
        self.logger.info("Reading file: %s", format_path(filename))
        handle = open(filename)
        contents = handle.read()
        handle.close()
        num_lines = len(contents.splitlines())
        self.logger.debug("Read %i line%s from %s",
                          num_lines, '' if num_lines == 1 else 's',
                          format_path(filename))
        return contents.rstrip()

    def write_file(self, filename, contents):
        """
        Write a text file and optionally provide feedback to the user.
        """
        self.logger.info("Writing file: %s", format_path(filename))
        handle = open(filename, 'w')
        handle.write(contents.rstrip() + "\n")
        handle.close()
        num_lines = len(contents.splitlines())
        self.logger.debug("Wrote %i line%s to %s", num_lines, '' if num_lines == 1 else 's', format_path(filename))
        return contents

    def hash_contents(self):
        """
        Hash the text file using the SHA1 algorithm.
        """
        self.logger.debug("Calculating SHA1 of %s", format_path(self.filename))
        handle = open(self.filename)
        context = hashlib.sha1()
        context.update(handle.read())
        handle.close()
        hexdigest = context.hexdigest()
        self.logger.debug("SHA1 of %s is %s", format_path(self.filename), hexdigest)
        return hexdigest

    @property
    def checksum_file(self):
        """
        Get the file where the checksum of the generated file is stored.
        """
        return os.path.join(self.directory, '.checksum')

    @property
    def directory(self):
        """
        Get the directory containing the modularized files.
        """
        return "%s.d" % self.filename

class RefuseToOverwrite(Exception):
    """
    Custom exception that is raised when update-dotdee notices that a generated
    file was modified.
    """

# vim: ts=4 sw=4 et
