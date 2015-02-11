script_link="$( readlink "$0" )" || script_link="$0"
apparent_sdk_dir="${script_link%/*}"
if [[ "$apparent_sdk_dir" == "$script_link" ]]; then
  apparent_sdk_dir=.
fi
sdk_dir="$( builtin cd -P "$apparent_sdk_dir" && pwd -P )"
bin_path="$sdk_dir/bin"
export PATH=$bin_path:$PATH
