# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import sys
import logging
import os
import platform
from subprocess import Popen, PIPE

from docutils.core import publish_string
import bcdoc
from bcdoc.clidocs import ReSTDocument
from bcdoc.clidocs import ProviderDocumentEventHandler
from bcdoc.clidocs import ServiceDocumentEventHandler
from bcdoc.clidocs import OperationDocumentEventHandler
import bcdoc.clidocevents
from bcdoc.textwriter import TextWriter

from awscli.argprocess import ParamShorthand


LOG = logging.getLogger('awscli.help')


def get_renderer():
    """
    Return the appropriate HelpRenderer implementation for the
    current platform.
    """
    if platform.system() == 'Windows':
        return WindowsHelpRenderer()
    else:
        return PosixHelpRenderer()


class HelpRenderer(object):
    """
    Interface for a help renderer.

    The renderer is responsible for displaying the help content on
    a particular platform.
    """

    def render(self, contents):
        """
        Each implementation of HelpRenderer must implement this
        render method.
        """
        pass


class PosixHelpRenderer(HelpRenderer):
    """
    Render help content on a Posix-like system.  This includes
    Linux and MacOS X.
    """

    PAGER = 'more'

    def get_pager_cmdline(self):
        pager = self.PAGER
        if 'MANPAGER' in os.environ:
            pager = os.environ['MANPAGER']
        elif 'PAGER' in os.environ:
            pager = os.environ['PAGER']
        return pager.split()

    def render(self, contents):
        cmdline = ['rst2man.py']
        LOG.debug("Running command: %s", cmdline)
        p2 = Popen(cmdline, stdin=PIPE, stdout=PIPE)
        p2.stdin.write(contents)
        p2.stdin.close()
        cmdline = ['groff', '-man', '-T', 'ascii']
        LOG.debug("Running command: %s", cmdline)
        p3 = Popen(cmdline, stdin=p2.stdout, stdout=PIPE)
        cmdline = self.get_pager_cmdline()
        LOG.debug("Running command: %s", cmdline)
        p4 = Popen(cmdline, stdin=p3.stdout)
        p4.communicate()
        sys.exit(1)


class WindowsHelpRenderer(HelpRenderer):
    """
    Render help content on a Windows platform.
    """

    def render(self, contents):
        text_output = publish_string(contents,
                                     writer=TextWriter())
        sys.stdout.write(text_output.decode('utf-8'))
        sys.exit(1)


class RawRenderer(HelpRenderer):
    """
    Render help as the raw ReST document.
    """

    def render(self, contents):
        sys.stdout.write(contents)
        sys.exit(1)


class HelpCommand(object):
    """
    HelpCommand Interface
    ---------------------
    A HelpCommand object acts as the interface between objects in the
    CLI (e.g. Providers, Services, Operations, etc.) and the documentation
    system (bcdoc).

    A HelpCommand object wraps the object from the CLI space and provides
    a consistent interface to critical information needed by the
    documentation pipeline such as the object's name, description, etc.

    The HelpCommand object is passed to the component of the
    documentation pipeline that fires documentation events.  It is
    then passed on to each document event handler that has registered
    for the events.

    All HelpCommand objects contain the following attributes:

        + ``session`` - A ``botocore`` ``Session`` object.
        + ``obj`` - The object that is being documented.
        + ``command_table`` - A dict mapping command names to
              callable objects.
        + ``arg_table`` - A dict mapping argument names to callable objects.
        + ``doc`` - A ``Document`` object that is used to collect the
              generated documentation.

    In addition, please note the `properties` defined below which are
    required to allow the object to be used in the document pipeline.

    Implementations of HelpCommand are provided here for Provider,
    Service and Operation objects.  Other implementations for other
    types of objects might be needed for customization in plugins.
    As long as the implementations conform to this basic interface
    it should be possible to pass them to the documentation system
    and generate interactive and static help files.
    """

    EventHandlerClass = None
    """
    Each subclass should define this class variable to point to the
    EventHandler class used by this HelpCommand.
    """

    def __init__(self, session, obj, command_table, arg_table):
        self.session = session
        self.obj = obj
        self.command_table = command_table
        self.arg_table = arg_table
        self.renderer = get_renderer()
        self.doc = ReSTDocument(target='man')

    @property
    def event_class(self):
        """
        Return the ``event_class`` for this object.

        The ``event_class`` is used by the documentation pipeline
        when generating documentation events.  For the event below::

            doc-title.<event_class>.<name>

        The document pipeline would use this property to determine
        the ``event_class`` value.
        """
        pass

    @property
    def name(self):
        """
        Return the name of the wrapped object.

        This would be called by the document pipeline to determine
        the ``name`` to be inserted into the event, as shown above.
        """
        pass

    def __call__(self, args, parsed_globals):
        # Create an event handler for a Provider Document
        self.EventHandlerClass(self)
        # Now generate all of the events for a Provider document.
        # We pass ourselves along so that we can, in turn, get passed
        # to all event handlers.
        bcdoc.clidocevents.generate_events(self.session, self)
        self.renderer.render(self.doc.getvalue())


class ProviderHelpCommand(HelpCommand):
    """Implements top level help command.

    This is what is called when ``aws help`` is run.

    """
    EventHandlerClass = ProviderDocumentEventHandler

    def __init__(self, session, command_table, arg_table,
                 description, synopsis, usage):
        HelpCommand.__init__(self, session, session.provider,
                             command_table, arg_table)
        self.description = description
        self.synopsis = synopsis
        self.help_usage = usage

    @property
    def event_class(self):
        return 'Provider'

    @property
    def name(self):
        return self.obj.name


class ServiceHelpCommand(HelpCommand):
    """Implements service level help.

    This is the object invoked whenever a service command
    help is implemented, e.g. ``aws ec2 help``.

    """

    EventHandlerClass = ServiceDocumentEventHandler

    def __init__(self, session, obj, command_table, arg_table, name,
                 event_class):
        super(ServiceHelpCommand, self).__init__(session, obj, command_table,
                                                 arg_table)
        self._name = name
        self._event_class = event_class

    @property
    def event_class(self):
        return self._event_class

    @property
    def name(self):
        return self._name


class OperationHelpCommand(HelpCommand):
    """Implements operation level help.

    This is the object invoked whenever help for a service is requested,
    e.g. ``aws ec2 describe-instances help``.

    """
    EventHandlerClass = OperationDocumentEventHandler

    def __init__(self, session, service, operation, arg_table, name,
                 event_class):
        HelpCommand.__init__(self, session, operation, None, arg_table)
        self.service = service
        self.param_shorthand = ParamShorthand()
        self._name = name
        self._event_class = event_class

    @property
    def event_class(self):
        return self._event_class

    @property
    def name(self):
        return self._name
