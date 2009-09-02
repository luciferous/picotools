# = Example .xsession
#
#   while true
#   do
#     xsetroot -name "`dwm-statusbar.sh`"
#     sleep 1m
#   done |
#   exec dwm
#
# = Example output
#
#   [wlan0] Wed 09/02/09 4:00pm 84% 0.18
#
routes=`ip link |grep state\ UP| awk '{ print $2 }' | tr -d : | xargs`
out="[$routes] `date '+%a %D %l:%M%P'` `acpi -b|awk '{print $4}'|sed 's/,//g'` `cat /proc/loadavg|awk '{print $1}'`"
echo `echo $out | tr -s \ `
