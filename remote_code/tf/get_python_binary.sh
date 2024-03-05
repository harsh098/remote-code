#!/usr/bin/env sh
echo -e "{\n \"python\": \"$(which python || which python3)\"\n}" | jq .