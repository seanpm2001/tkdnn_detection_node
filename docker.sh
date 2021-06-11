#!/usr/bin/env bash

if [ $# -eq 0 ]
then
    echo "Usage:"
    echo
    echo "  `basename $0` (b | build)        Build"
    echo "  `basename $0` (u | up)           Run or Start"
    echo "  `basename $0` (r | rm)           Remove Container"
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
        docker kill tkdnn_detector
        docker rm tkdnn_detector # remove existing container
        docker build . -t zauberzeug/tkdnn_detection_node:latest $cmd_args
        ;;
    u | up)
        docker start tkdnn_detector || nvidia-docker run -d -v $(pwd):/app --name tkdnn_detector --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all -p 80:80 -v /usr/bin/qemu-arm-static:/usr/bin/qemu-arm-static zauberzeug/tkdnn_detection_node:latest $cmd_args
        ;;
    s | stop)
        docker stop tkdnn_detector $cmd_args
        ;;
    k | kill)
        docker kill tkdnn_detector $cmd_args
        ;;
    r | rm)
        docker kill tkdnn_detector
        docker rm tkdnn_detector $cmd_args
        ;;
    l | log | logs)
        docker logs -f --tail 100 $cmd_args tkdnn_detector
        ;;
    e | exec)
        docker exec $cmd_args tkdnn_detector
        ;;
    a | attach)
        docker exec -it $cmd_args tkdnn_detector /bin/bash
        ;;
    *)
        echo "Unsupported command \"$cmd\""
        exit 1
esac

