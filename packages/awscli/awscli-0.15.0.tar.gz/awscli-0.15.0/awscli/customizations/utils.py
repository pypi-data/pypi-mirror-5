# Copyright 2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
Utility functions to make it easier to work with customizations.

"""
def rename_argument(argument_table, existing_name, new_name):
    current = argument_table[existing_name]
    argument_table[new_name] = current
    current.name = new_name
    del argument_table[existing_name]


def rename_command(command_table, existing_name, new_name):
    current = command_table[existing_name]
    command_table[new_name] = current
    current.name = new_name
    del command_table[existing_name]
