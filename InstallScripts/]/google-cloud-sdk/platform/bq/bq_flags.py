#!/usr/bin/env python
"""Flags for calling BigQuery."""

import os


import gflags as flags

FLAGS = flags.FLAGS
flags.DEFINE_string(
    'apilog', None,
    'Turn on logging of all server requests and responses. If no string is '
    'provided, log to stdout; if a string is provided, instead log to that '
    'file.')
flags.DEFINE_string(
    'api',
    'https://www.googleapis.com',
    'API endpoint to talk to.')
flags.DEFINE_string(
    'api_version', 'v2',
    'API version to use.')
flags.DEFINE_boolean(
    'debug_mode', False,
    'Show tracebacks on Python exceptions.')
flags.DEFINE_string(
    'trace', None,
    'A tracing token of the form "token:<token>" '
    'to include in api requests.')

flags.DEFINE_string(
    'bigqueryrc', os.path.join(os.path.expanduser('~'), '.bigqueryrc'),
    'Path to configuration file. The configuration file specifies '
    'new defaults for any flags, and can be overrridden by specifying the '
    'flag on the command line. If the --bigqueryrc flag is not specified, the '
    'BIGQUERYRC environment variable is used. If that is not specified, the '
    'path "~/.bigqueryrc" is used.')
flags.DEFINE_string(
    'credential_file', os.path.join(os.path.expanduser('~'),
    '.bigquery.v2.token'),
    'Filename used for storing the BigQuery OAuth token.')
flags.DEFINE_string(
    'discovery_file', '',
    'Filename for JSON document to read for discovery.')
flags.DEFINE_boolean(
    'synchronous_mode', True,
    'If True, wait for command completion before returning, and use the '
    'job completion status for error codes. If False, simply create the '
    'job, and use the success of job creation as the error code.',
    short_name='sync')
flags.DEFINE_string(
    'project_id', '',
    'Default project to use for requests.')
flags.DEFINE_string(
    'dataset_id', '',
    'Default dataset to use for requests. (Ignored when not applicable.)')
# This flag is "hidden" at the global scope to avoid polluting help
# text on individual commands for rarely used functionality.
flags.DEFINE_string(
    'job_id', None,
    'A unique job_id to use for the request. If not specified, this client '
    'will generate a job_id. Applies only to commands that launch jobs, '
    'such as cp, extract, link, load, and query.')
flags.DEFINE_boolean(
    'fingerprint_job_id', False,
    'Whether to use a job id that is derived from a fingerprint of the job '
    'configuration. This will prevent the same job from running multiple times '
    'accidentally.')
flags.DEFINE_boolean(
    'quiet', False,
    'If True, ignore status updates while jobs are running.',
    short_name='q')
flags.DEFINE_boolean(
    'headless',
    False,
    'Whether this bq session is running without user interaction. This '
    'affects behavior that expects user interaction, like whether '
    'debug_mode will break into the debugger and lowers the frequency '
    'of informational printing.')
flags.DEFINE_enum(
    'format', None,
    ['none', 'json', 'prettyjson', 'csv', 'sparse', 'pretty'],
    'Format for command output. Options include:'
    '\n pretty: formatted table output'
    '\n sparse: simpler table output'
    '\n prettyjson: easy-to-read JSON format'
    '\n json: maximally compact JSON'
    '\n csv: csv format with header'
    '\nThe first three are intended to be human-readable, and the latter '
    'three are for passing to another program. If no format is selected, '
    'one will be chosen based on the command run.')
flags.DEFINE_multistring(
    'job_property', None,
    'Additional key-value pairs to include in the properties field of '
    'the job configuration')  # No period: Multistring adds flagspec suffix.
flags.DEFINE_boolean(
    'use_gce_service_account', False,
    'Use this when running on a Google Compute Engine instance to use service '
    'account credentials instead of stored credentials. For more information, '
    'see: https://developers.google.com/compute/docs/authentication')
flags.DEFINE_string(
    'service_account', '',
    'Use this service account email address for authorization. '
    'For example, 1234567890@developer.gserviceaccount.com.'
    )
flags.DEFINE_string(
    'service_account_private_key_file', '',
    'Filename that contains the service account private key. '
    'Required if --service_account is specified.')
flags.DEFINE_string(
    'service_account_private_key_password', 'notasecret',
    'Password for private key. This password must match the password '
    'you set on the key when you created it in the Google APIs Console. '
    'Defaults to the default Google APIs Console private key password.')
flags.DEFINE_string(
    'service_account_credential_file', None,
    'File to be used as a credential store for service accounts. '
    'Must be set if using a service account.')
flags.DEFINE_integer(
    'max_rows_per_request', None,
    'Specifies the max number of rows to return per read.')
