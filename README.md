# Detection Node

This is a node for the Learning Loop wich provides an RESTful API for edge devices to retrieve inferences.
It is intended to run on NVidia Jetson (>= r32.4.4) by utilizing TKDNN for now.

# Features

- Active Learning for the Zauberzeug Learning Loop (upload images & detections with bad predictions)
- RESTful interface to retrieve predictions

## Usage

Runs only on NVidia Jetson (Tegra Architecture).

```bash
docker run --name detector --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all -p 80:80 -v model:/model zauberzeug/tkdnn-detection_node:latest
```
