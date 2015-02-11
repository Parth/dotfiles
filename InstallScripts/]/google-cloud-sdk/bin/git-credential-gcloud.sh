#!/bin/sh
#
# Copyright 2013 Google Inc. All Rights Reserved.
#


# <cloud-sdk-sh-preamble>
#
#  CLOUDSDK_ROOT_DIR            (a)  installation root dir
#  CLOUDSDK_PYTHON              (u)  python interpreter path
#  CLOUDSDK_PYTHON_ARGS         (u)  python interpreter arguments
#  CLOUDSDK_PYTHON_SITEPACKAGES (u)  use python site packages
#
# (a) always defined by the preamble
# (u) user definition overrides preamble

# Determines the real cloud sdk root dir given the script path.
# Would be easier with a portable "readlink -f".
_cloudsdk_root_dir() {
  case $1 in
  /*)   _cloudsdk_path=$1
        ;;
  */*)  _cloudsdk_path=$PWD/$1
        ;;
  *)    _cloudsdk_path=$(which "$1")
        case $_cloudsdk_path in
        /*) ;;
        *)  _cloudsdk_path=$PWD/$_cloudsdk_path ;;
        esac
        ;;
  esac
  _cloudsdk_dir=0
  while :
  do
    while _cloudsdk_link=$(readlink "$_cloudsdk_path")
    do
      case $_cloudsdk_link in
      /*) _cloudsdk_path=$_cloudsdk_link ;;
      *)  _cloudsdk_path=$(dirname "$_cloudsdk_path")/$_cloudsdk_link ;;
      esac
    done
    case $_cloudsdk_dir in
    1)  break ;;
    esac
    _cloudsdk_dir=1
    _cloudsdk_path=$(dirname "$_cloudsdk_path")
  done
  while :
  do  case $_cloudsdk_path in
      */.)    _cloudsdk_path=$(dirname "$_cloudsdk_path")
              ;;
      */bin)  dirname "$_cloudsdk_path"
              break
              ;;
      *)      echo "$_cloudsdk_path"
              break
              ;;
      esac
  done
}
CLOUDSDK_ROOT_DIR=$(_cloudsdk_root_dir "$0")

# if CLOUDSDK_PYTHON is not empty
[ -z "$CLOUDSDK_PYTHON" ] &&
  CLOUDSDK_PYTHON=python

# if CLOUDSDK_PYTHON_SITEPACKAGES and VIRTUAL_ENV are empty
case :$CLOUDSDK_PYTHON_SITEPACKAGES:$VIRTUAL_ENV: in
:::)  # add -S to CLOUDSDK_PYTHON_ARGS if not already there
      case " $CLOUDSDK_PYTHON_ARGS " in
      *" -S "*) ;;
      "  ")     CLOUDSDK_PYTHON_ARGS="-S"
                ;;
      *)        CLOUDSDK_PYTHON_ARGS="$CLOUDSDK_PYTHON_ARGS -S"
                ;;
      esac
      unset CLOUDSDK_PYTHON_SITEPACKAGES
      ;;
*)    # remove -S from CLOUDSDK_PYTHON_ARGS if already there
      case " $CLOUDSDK_PYTHON_ARGS " in
      *" -S "*) CLOUDSDK_PYTHON_ARGS=${CLOUDSDK_PYTHON_ARGS/-S/} ;;
      esac
      # if CLOUDSDK_PYTHON_SITEPACKAGES is empty
      [ -z "$CLOUDSDK_PYTHON_SITEPACKAGES" ] &&
        CLOUDSDK_PYTHON_SITEPACKAGES=1
      export CLOUDSDK_PYTHON_SITEPACKAGES
      ;;
esac

export CLOUDSDK_ROOT_DIR CLOUDSDK_PYTHON_ARGS

# </cloud-sdk-sh-preamble>


export CLOUDSDK_COMPONENT_MANAGER_DISABLE_UPDATE_CHECK=1

"${CLOUDSDK_ROOT_DIR}/bin/gcloud" auth git-helper --ignore-unknown "$@"
