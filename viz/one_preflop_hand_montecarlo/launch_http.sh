if [ "$1" = "" ] ; then
	# http-server -p 8080 &
	python -m SimpleHTTPServer 8080 &
	open http://localhost:8080
else
	# http-server -p "$1" &
	python -m SimpleHTTPServer "$1" &
	open http://localhost:"$1"
fi
