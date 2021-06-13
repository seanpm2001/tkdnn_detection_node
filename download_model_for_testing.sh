#!/bin/bash

echo "NOTE: call this script from the host."

TARGET_PATH='data'

rsync -ravh --copy-links zauberzeug@185.21.101.186:~/learning-loop-dev/projects/absammel_roboter/models/yolo4_tiny_3lspp_12_76844/ $TARGET_PATH
mv $TARGET_PATH/training_best_mAP_0.898879_iteration_76844_avgloss_2.452776_.weights $TARGET_PATH/weightfile.weights
rsync -ravh --copy-links zauberzeug@185.21.101.186:~/learning-loop-dev/projects/absammel_roboter/data/2020-03-17_22-21-09/j16/recordings/b4e62da43a85_2020-03-16_16-46-20.031.jpg $TARGET_PATH/test.jpg
