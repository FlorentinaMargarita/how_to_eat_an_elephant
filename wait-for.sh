#!/bin/sh

set -e

echo "nc path: $(which nc)"

host="$1"
shift
port="$1"
shift
cmd="$@"

until nc -z -v -w30 "$host" "$port"; do
  echo "Waiting for $host:$port..."
  sleep 1
done

exec $cmd