#!/bin/sh
while inotifywait -e modify less/wifarer less/bootstrap; do
  lessc less/all.less > css/style.css
done
