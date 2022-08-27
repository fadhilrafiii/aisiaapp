import pandas as pd
import logging
from PIL import Image
import glob
import os
import pycocotools
import numpy as np
import torch
import time
import torch.utils.data
import pandas as pd
from torchvision import transforms
import torchvision
import torchvision.models.detection.ssdlite
import torch.nn as nn
from functools import partial
from torchvision.models.detection import _utils as det_utils
from torchvision.models.detection.ssdlite import SSDLiteClassificationHead
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

logger = logging.getLogger(__name__)

def get_model_faster_rcnn(num_classes):
  # load an object detection model pre-trained on COCO
  model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights='FasterRCNN_ResNet50_FPN_Weights.DEFAULT', trainable_backbone_layers=0, box_nms_thresh=0.3, box_score_thresh=0.4)
  # get the number of input features for the classifier
  in_features = model.roi_heads.box_predictor.cls_score.in_features
  # replace the pre-trained head with a new on
  model.roi_heads.box_predictor = FastRCNNPredictor(in_features,num_classes)
  return model

def get_model_mobilenet(num_classes):
  # load an object detection model pre-trained on COCO
  model = torchvision.models.detection.ssdlite320_mobilenet_v3_large(pretrained = True, trainable_backbone_layers=0)
  model.nms_thresh=0.2
  model.score_thresh=0.2
  # get the number of input features for the classifier
  in_channels = det_utils.retrieve_out_channels(model.backbone, (320, 320))
  num_anchors = model.anchor_generator.num_anchors_per_location()
  norm_layer  = partial(nn.BatchNorm2d, eps=0.001, momentum=0.03)
  # replace the pre-trained head with a new on
  model.head.classification_head = SSDLiteClassificationHead(in_channels, num_anchors, num_classes, norm_layer)
  return model

image_test = "../assets/000000581913_flip_h.jpg"

def get_predictions(image, model_type):
  if (model_type == 'MobileNet'):
    WEIGHT_PATH= "assets/mobilenet_sgd.pt"
    model = get_model_mobilenet(num_classes = 39)
    model.load_state_dict(torch.load(WEIGHT_PATH, map_location=torch.device('cpu')))
  else:
    WEIGHT_PATH= "assets/faster_rcnn_sgd.pt"
    model = get_model_faster_rcnn(num_classes = 39)
    model.load_state_dict(torch.load(WEIGHT_PATH, map_location=torch.device('cpu')))

  img = Image.open(image).convert("RGB")
  tensor_transformer = transforms.ToTensor()
  img_trans = tensor_transformer(img)
  idx = 2

  model.eval()
  start_time = time.time()
  with torch.no_grad():
      prediction = model([img_trans])
  end_time = time.time()

  inference_time = end_time - start_time
  logger.info(f'Time needed for inference: {inference_time} second(s)')

  class_name= pd.read_csv('assets/coco_classes38.txt', header=None, names=['classname'])
  preds=[]
  for i in range(len(prediction[0]['labels'])):
    tmp=[]
    tmp.append(i)
    tmp.append(float(prediction[0]['boxes'][i][1].numpy()))
    preds.append(tmp)
  preds.sort(key=lambda x: x[1])
  result=[]
  for i in range(len(preds)):
    idx = preds[i][0]
    class_idx=prediction[0]['labels'][idx].numpy()
    result.append({'box':prediction[0]['boxes'][idx].numpy(), 'label':class_name['classname'][class_idx-1]}) 

  return result