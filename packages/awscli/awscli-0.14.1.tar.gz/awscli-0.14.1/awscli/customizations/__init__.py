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
"""
Customizations
==============

As we start to accumulate more and more of these *built-in* customizations
we probably need to come up with some way to organize them and to make
it easy to add them and register them.

One idea I had was to place them all with a package like this.  That
at least keeps them all in one place.  Each module in this package
should contain a single customization (I think).

To take it a step further, we could have each module define a couple
of well-defined attributes:

* ``EVENT`` would be a string containing the event that this customization
  needs to be registered with.  Or, perhaps this should be a list of
  events?
* ``handler`` is a callable that will be registered as the handler
  for the event.

Using a convention like this, we could perhaps automatically discover
all customizations and register them without having to manually edit
``handlers.py`` each time.
"""
from awscli.clidriver import BaseCLIArgument


class CustomArgument(BaseCLIArgument):

    Documentation = 'Documentation goes here'

    def __init__(self, operation, name, cli_type_name='string',
                 documentation=None, default=None):
        super(CustomArgument, self).__init__(
            name, argument_object=None)
        self._operation = operation
        self._name = name
        self._cli_type_name = cli_type_name
        self._documentation = documentation
        self._default = default

    @property
    def cli_name(self):
        return '--' + self._name

    @property
    def cli_type_name(self):
        return self._cli_type_name

    @property
    def required(self):
        return False

    @property
    def documentation(self):
        return self._documentation

    def add_to_parser(self, parser, cli_name=None):
        parser.add_argument(self.cli_name, dest=self._name,
                            default=self._default)

    def add_to_params(self, parameters, value):
        pass

