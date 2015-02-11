# Copyright 2015 Google Inc. All Rights Reserved.

"""Script for reporting gcloud metrics."""

import os
import pickle
import sys

import httplib2


def ReportMetrics(metrics_file_path):
  """Sends the specified anonymous usage event to the given analytics endpoint.

  Args:
      metrics_file_path: str, File with pickled metrics (list of tuples).
  """
  with open(metrics_file_path, 'rb') as metrics_file:
    metrics = pickle.load(metrics_file)
  os.remove(metrics_file_path)

  http = httplib2.Http()
  for metric in metrics:
    headers = {'user-agent': metric[2]}
    http.request(metric[0], method='POST', body=metric[1], headers=headers)

if __name__ == '__main__':
  try:
    ReportMetrics(sys.argv[1])
  # pylint: disable=bare-except, Never fail or output a stacktrace here.
  except:
    pass
