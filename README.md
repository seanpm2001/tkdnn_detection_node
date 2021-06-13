# Detection Node

This is a node for the Learning Loop wich provides an RESTful API for edge devices to retrieve inferences.
It is intended to run on NVidia Jetson (>= r32.4.4) by utilizing TKDNN for now.

# Features

- Active Learning for the Zauberzeug Learning Loop (upload images & detections with bad predictions)
- RESTful interface to retrieve predictions

## Usage

Runs only on NVidia Jetson (Tegra Architecture).

```bash
docker pull zauberzeug/tkdnn_detection_node:latest # to make sure we have the latest image
docker run -it --rm --runtime=nvidia -p 80:80 \
-v $(pwd)/data:/data \          # bind the model to make it persistent (should contain an model.rt file)
-e NVIDIA_VISIBLE_DEVICES=all \ # to enable hardware acceleration
-e ORGANIZATION=zauberzeug \    # define your organization
-e PROJECT=demo\                # define the project for which the detector should run
zauberzeug/tkdnn_detection_node:latest
```

If the container is up and running you can get detections through the RESTful API:

```bash
curl --request POST -H 'mac: FF:FF' -F 'file=@test.jpg' localhost/detect
```

## Development

Put a TensorRT model `model.rt` and a `names.txt` with the category names into the `data` folder.
You can use the `download_model_for_testing.sh` helper.

Build the container with `./docker.sh build` and run it with `./docker.sh run`.
Now you can connect to the container with vs code and modify the code.
