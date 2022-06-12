#!/bin/bash
JSON_DATA='[{"k": "a"}, {"k": "a", "k1": "alt"}, {"k": "b"}, {"k": "c"}]'
echo "$JSON_DATA" | jq '.[] | select(.k | IN(["a", "b"][]))'

# With or statements
echo "$JSON_DATA" | jq '.[] | select(.k == "a" or .k == "b")'

# With weird dict-like statement
echo "$JSON_DATA" | jq '.[] | select(.k | in({"a": 1, "b": 1}))'

echo "$JSON_DATA" | jq '.[] | select(.k | IN(["a", "b"][]))'

echo "$JSON_DATA" | jq '.[] | select(any(["a", "b"] == .k; .))'

echo "$JSON_DATA" | jq '.[] | select(.k | index(["a", "b"]))'
echo "$JSON_DATA" | jq '.[] | select(.k | contains(["a", "b"]))'
