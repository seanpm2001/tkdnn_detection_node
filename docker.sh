#!/usr/bin/env bash

if [ $# -eq 0 ]
then
    echo "Usage:"
    echo
    echo "  `basename $0` (b | build)        Build"
    echo "  `basename $0` (r | run)          Run"
    echo "  `basename $0` (s | stop)         Stop"
    echo "  `basename $0` (k | kill)         Kill"
    echo "  `basename $0` rm                 Remove"
    echo
    echo "  `basename $0` (l | log)                 Show log tail (last 100 lines)"
    echo "  `basename $0` (e | exec)     <command>  Execute command"
    echo "  `basename $0` (a | attach)              Attach to container with shell"
    echo
    echo "Arguments:"
    echo
    echo "  command       Command to be executed inside a container"
    exit
fi

cmd=$1
cmd_args=${@:2}
case $cmd in
    b | build)
        docker build . -t tkdnn_detection_node $cmd_args
        ;;
    r | run)
        docker run -it -v $(pwd):/app --name tkdnn_detection_node tkdnn_detection_node $cmd_args
        ;;
    s | stop)
        docker stop tkdnn_detection_node $cmd_args
        ;;
    k | kill)
        docker kill tkdnn_detection_node $cmd_args
        ;;
    l | log | logs)
        docker logs -f --tail 100 $cmd_args tkdnn_detection_node
        ;;
    e | exec)
        docker exec $cmd_args tkdnn_detection_node
        ;;
    a | attach)
        docker exec $cmd_args tkdnn_detection_node /bin/bash
        ;;
    *)
        echo "Unsupported command \"$cmd\""
        exit 1
esac

