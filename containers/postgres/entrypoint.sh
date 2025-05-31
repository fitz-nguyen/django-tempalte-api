#!/bin/sh
cmd="$@"

if [ -z "${POSTGRES_USER}" ]; then
    # the official postgres image uses 'postgres' as default user if not set explictly.
    export POSTGRES_USER=postgres
fi

exec $cmd
