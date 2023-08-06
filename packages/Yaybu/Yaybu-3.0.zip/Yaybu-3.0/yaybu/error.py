# Copyright 2013 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

Classes that represent errors within yaybu.

What is listed here are the exceptions raised within Python, with an
explanation of their meaning. If you wish to detect a specific error on
invocation, you can do so via the return code of the yaybu process.

All yaybu errors have a returncode, which is returned from the yaybu program
if these errors occur. This is primarily for the test harness, but feel free
to rely on these, they should be stable.

A returncode of less than 128 is an error from within the range specified in
the errno library, which contains the standard C error codes.

These may have been actually returned from a shell command, or they may be
based on our interpretation of the failure mode they represent. Resources will
define the errors they may return. """

import errno
from yay.errors import ParseError, NoMatching, EvaluationError

ParseError.returncode = 128

class BindingError(ParseError):
    """ An error during policy binding. """

    returncode = 129
    """ returns error code 129 to the invoking environment. """

class ExecutionError(EvaluationError):
    """ Root of exceptions that are caused by execution failing in an unexpected way. """
    returncode = 130
    """ returns error code 130 to the invoking environment. """

class DpkgError(ExecutionError):
    """ dpkg returned something other than 0 or 1 """
    returncode = 131
    """ returns error code 131 to the invoking environment. """

class AptError(ExecutionError):
    """ An apt command failed unrecoverably. """
    returncode = 132
    """ returns error code 132 to the invoking environment. """

class CommandError(ExecutionError):
    """ A command from the Execute provider did not return the expected return
    code. """
    returncode = 133
    """ returns error code 133 to the invoking environment. """

class NoValidPolicy(ParseError):
    """ There is no valid policy for the resource. """

    returncode = 135
    """ returns error code 135 to the invoking environment. """

class NonConformingPolicy(ParseError):
    """ A policy has been specified, or has been chosen by default, but the
    parameters provided for the resource do not match those required for the
    policy. Check the documentation to ensure you have provided all required
    parameters. """
    returncode = 136
    """ returns error code 136 to the invoking environment. """

class NoSuitableProviders(ParseError):
    """ There are no suitable providers available for the policy and resource
    chosen. This may be because a provider has not been written for this
    Operating System or service, or it may be that you have not specified the
    parameters correctly. """
    returncode = 137
    """ returns error code 137 to the invoking environment. """

class TooManyProviders(ParseError):
    """ More than one provider matches the specified resource, and Yaybu is unable to choose between them. """
    returncode = 138
    """ returns error code 138 to the invoking environment. """

class InvalidProvider(ExecutionError):
    """ A provider is not valid. This is detected before any changes have been
    applied. """
    returncode = 139
    """ returns error code 139 to the invoking environment. """

class InvalidGroup(ExecutionError):
    """ The specified user group does not exist. """
    returncode = 140
    """ returns error code 140 to the invoking environment. """

class InvalidUser(ExecutionError):
    """ The specified user does not exist. """
    returncode = 141
    """ returns error code 141 to the invoking environment. """

class OperationFailed(ExecutionError):
    """ A general failure of an operation. For example, we tried to create a
    symlink, everything appeared to work but then a link does not exist. This
    should probably never happen. """
    returncode = 142
    """ returns error code 142 to the invoking environment. """

class BinaryMissing(ExecutionError):
    """ A specific error for an expected binary (ln, rm, etc.) not being
    present where expected. """
    returncode = 143
    """ returns error code 143 to the invoking environment. """

class DanglingSymlink(ExecutionError):
    """ The destination of a symbolic link does not exist. """
    returncode = 144
    """ returns error code 144 to the invoking environment. """

class UserAddError(ExecutionError):
    """ An error from the useradd command. It has a bunch of error codes of
    it's own. """
    returncode = 145
    """ returns error code 145 to the invoking environment. """

class PathComponentMissing(ExecutionError):
    """ A component of the path is not present """
    returncode = 146
    """ returns error code 146 to the invoking environment. """

class PathComponentNotDirectory(ExecutionError):
    """ A component of the path is in fact not a directory """
    returncode = 147
    """ returns error code 147 to the invoking environment. """

class SavedEventsAndNoInstruction(ExecutionError):
    """ There is a saved events file and the user has not decided what to do
    about it. Invoke with --resume or --no-resume. """
    returncode = 148
    """ returns error code 148 to the invoking environment. """

class MissingAsset(ExecutionError):
    """ An asset referenced by a resource could not be found on the Yaybu
    search path. """
    returncode = 149
    """ returns error code 149 to the invoking environment. """

class CheckoutError(ExecutionError):
    """ An insurmountable problem was encountered during checkout """
    returncode = 150
    """ returns error code 150 to the invoking environment. """

class Incompatible(ExecutionError):
    """ An incompatibility was detected and execution can't continue """
    returncode = 151

class MissingDependency(ExecutionError):
    """ A dependency required for a feature or provider is missing """
    returncode = 152

class UnmodifiedAsset(ExecutionError):
    """ An asset was requested unnecesarily. This indicates an error in cache
    handling and should be filed as a bug against Yaybu. """
    returncode = 153

class ArgParseError(ParseError):
    """ Error parsing an argument that was applied to a config """
    returncode = 154

class TemplateError(ParseError):
    """ Error handling a template """
    returncode = 155

class InvalidCredsError(ExecutionError):
    """ Invalid credentials """
    returncode = 156

class NothingChanged(ExecutionError):
    """ Not really an error, but we need to know if this happens for our
    tests. This exception is never really raised, but it's useful to keep the
    error code here!"""
    returncode = 254
    """ returns error code 254 to the invoking environment. """

class ConnectionError(ExecutionError):
    """ An error occured while establishing a remote connection """
    returncode = 255

class SystemError(ExecutionError):
    """ An error represented by something in the errno list. """

    def __init__(self, returncode, stdout=None, stderr=None):
        # if the returncode is not in errno, this will blow up.
        try:
            self.msg = errno.errorcode[returncode]
        except KeyError:
            self.msg = "Exit code %s" % returncode
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

