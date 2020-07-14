#!/usr/bin/expect

# see https://stackoverflow.com/a/28293101/1887602

set timeout 20

set cmd [lrange $argv 1 end]
set password [lindex $argv 0]

eval spawn $cmd
expect "assword:"
send "$password\r";
interact
