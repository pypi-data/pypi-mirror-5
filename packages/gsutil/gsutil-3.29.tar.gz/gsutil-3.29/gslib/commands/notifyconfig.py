# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module provides the notifyconfig command to gsutil."""

import getopt
import uuid

from apiclient import discovery
import boto

from gslib.command import Command
from gslib.command import COMMAND_NAME
from gslib.command import COMMAND_NAME_ALIASES
from gslib.command import CONFIG_REQUIRED
from gslib.command import FILE_URIS_OK
from gslib.command import MAX_ARGS
from gslib.command import MIN_ARGS
from gslib.command import NO_MAX
from gslib.command import PROVIDER_URIS_OK
from gslib.command import SUPPORTED_SUB_ARGS
from gslib.command import URIS_START_ARG
from gslib.exception import CommandException
from gslib.help_provider import HELP_NAME
from gslib.help_provider import HELP_NAME_ALIASES
from gslib.help_provider import HELP_ONE_LINE_SUMMARY
from gslib.help_provider import HELP_TEXT
from gslib.help_provider import HELP_TYPE
from gslib.help_provider import HelpType


_detailed_help_text = ("""
<B>SYNOPSIS</B>
  gsutil notifyconfig watchbucket [-i id] [-t token] app_url bucket_uri...
  gsutil notifyconfig stopchannel channel_id resource_id


<B>DESCRIPTION</B>
  The notifyconfig command can be used to configure notifications.
  For more information on the Object Change Notification feature, please see:
  https://developers.google.com/storage/docs/object-change-notification

  The notifyconfig command has two sub-commands:

  watchbucket
    The watchbucket sub-command can be used to watch a bucket for object
    changes.

    The app_url parameter must be an HTTPS URL to an application that will be
    notified of changes to any object in the bucket.

    The optional id parameter can be used to assign a unique identifier to the
    created notification channel. If not provided, a random UUID string will be
    generated.

    The optional token parameter can be used to validate notifications events.
    To do this, set this custom token and store it to later verify that
    notification events contain the client token you expect.

  stopchannel
    The stopchannel sub-command can be used to stop sending change events to a
    notification channel.

    The channel_id and resource_id parameters should match the values from the
    response of a bucket watch request.


<B>EXAMPLES</B>

  Watch the bucket example-bucket for changes and send notifications to an
  application server running at example.com:

    gsutil notifyconfig watchbucket https://example.com/notify \\
      gs://example-bucket

  Assign identifier my-channel-id to the created notification channel:

    gsutil notifyconfig watchbucket -i my-channel-id \\
      https://example.com/notify gs://example-bucket

  Set a custom client token that will be included with each notification event:

    gsutil notifyconfig watchbucket -t my-client-token \\
      https://example.com/notify gs://example-bucket

  Stop the notification event channel with channel identifier channel1 and
  resource identifier SoGqan08XDIFWr1Fv_nGpRJBHh8:

    gsutil notifyconfig stopchannel channel1 SoGqan08XDIFWr1Fv_nGpRJBHh8

""")


DISCOVERY_SERVICE_URL = boto.config.get_value(
    'GSUtil', 'discovery_service_url', None)
JSON_API_VERSION = boto.config.get_value(
    'GSUtil', 'json_api_version', 'v1beta2')


class NotifyConfigCommand(Command):
  """Implementation of gsutil notifyconfig command."""

  # Command specification (processed by parent class).
  command_spec = {
      # Name of command.
      COMMAND_NAME: 'notifyconfig',
      # List of command name aliases.
      COMMAND_NAME_ALIASES: ['notify', 'notification', 'notifications'],
      # Min number of args required by this command.
      MIN_ARGS: 3,
      # Max number of args required by this command, or NO_MAX.
      MAX_ARGS: NO_MAX,
      # Getopt-style string specifying acceptable sub args.
      SUPPORTED_SUB_ARGS: 'i:t:',
      # True if file URIs acceptable for this command.
      FILE_URIS_OK: True,
      # True if provider-only URIs acceptable for this command.
      PROVIDER_URIS_OK: False,
      # Index in args of first URI arg.
      URIS_START_ARG: 1,
      # True if must configure gsutil before running command.
      CONFIG_REQUIRED: True,
  }
  help_spec = {
      # Name of command or auxiliary help info for which this help applies.
      HELP_NAME: 'notifyconfig',
      # List of help name aliases.
      HELP_NAME_ALIASES: ['watchbucket', 'stopchannel'],
      # Type of help:
      HELP_TYPE: HelpType.COMMAND_HELP,
      # One line summary of this help.
      HELP_ONE_LINE_SUMMARY: 'Configure object change notification',
      # The full help text.
      HELP_TEXT: _detailed_help_text,
  }

  def _WatchBucket(self):
    identifier = None
    client_token = None
    if self.sub_opts:
      for o, a in self.sub_opts:
        if o == '-i':
          identifier = a
        if o == '-t':
          client_token = a

    identifier = identifier or str(uuid.uuid4())
    watch_uri = self.args[0]
    bucket_arg = self.args[-1]

    if not watch_uri.lower().startswith('https://'):
      raise CommandException('The application URL must be an https:// URL.')

    bucket_uri = self.suri_builder.StorageUri(bucket_arg)
    if bucket_uri.get_provider().name != 'google':
      raise CommandException(
          'The %s command can only be used with gs:// bucket URIs.' %
          self.command_name)
    if not bucket_uri.names_bucket():
      raise CommandException('URI must name a bucket for the %s command.' %
                             self.command_name)

    self.logger.info('Watching bucket %s with application URL %s ...',
                     bucket_uri, watch_uri)

    bucket = bucket_uri.get_bucket()
    auth_handler = bucket.connection._auth_handler
    oauth2_client = getattr(auth_handler, 'oauth2_client', None)
    if not oauth2_client:
      raise CommandException(
          'The %s command requires using OAuth credentials.' %
          self.command_name)

    http = oauth2_client.CreateHttpRequest()
    kwargs = {'http': http}
    if DISCOVERY_SERVICE_URL:
      kwargs['discoveryServiceUrl'] = DISCOVERY_SERVICE_URL
    service = discovery.build(
        'storage', JSON_API_VERSION, **kwargs)

    body = {'type': 'WEB_HOOK',
            'address': watch_uri,
            'id': identifier}
    if client_token:
      body['token'] = client_token
    request = service.objects().watchAll(body=body, bucket=bucket.name)
    request.headers['authorization'] = oauth2_client.GetAuthorizationHeader()
    response = request.execute()

    channel_id = response['id']
    resource_id = response['resourceId']
    client_token = response['token']
    self.logger.info('Successfully created watch notification channel.')
    self.logger.info('Watch channel identifier: %s', channel_id)
    self.logger.info('Canonicalized resource identifier: %s', resource_id)
    self.logger.info('Client state token: %s', client_token)

    return 0

  def _StopChannel(self):
    channel_id = self.args[0]
    resource_id = self.args[1]

    uri = self.suri_builder.StorageUri('gs://')
    self.logger.info('Removing channel %s with resource identifier %s ...',
                     channel_id, resource_id)

    auth_handler = uri.connect()._auth_handler
    oauth2_client = getattr(auth_handler, 'oauth2_client', None)
    if not oauth2_client:
      raise CommandException(
          'The %s command requires using OAuth credentials.' %
          self.command_name)

    http = oauth2_client.CreateHttpRequest()
    kwargs = {'http': http}
    if DISCOVERY_SERVICE_URL:
      kwargs['discoveryServiceUrl'] = DISCOVERY_SERVICE_URL
    service = discovery.build(
        'storage', JSON_API_VERSION, **kwargs)

    body = {'id': channel_id,
            'resourceId': resource_id}
    request = service.channels().stop(body=body)
    request.headers['authorization'] = oauth2_client.GetAuthorizationHeader()
    request.execute()
    self.logger.info('Succesfully removed channel.')

    return 0

  def _RunSubCommand(self, func):
    try:
      (self.sub_opts, self.args) = getopt.getopt(
          self.args, self.command_spec[SUPPORTED_SUB_ARGS])
      func()
    except getopt.GetoptError, e:
      raise CommandException('%s for "%s" command.' % (e.msg,
                                                       self.command_name))

  def RunCommand(self):
    subcommand = self.args.pop(0)
    if subcommand == 'watchbucket':
      return self._RunSubCommand(self._WatchBucket)
    elif subcommand == 'stopchannel':
      return self._RunSubCommand(self._StopChannel)
    else:
      raise CommandException('Invalid subcommand "%s" for the %s command.' %
                             (subcommand, self.command_name))
