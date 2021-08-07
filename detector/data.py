import os
import logging
import json
import zipfile
import io
from learning_loop_node.detector.about import About


def ensure_model():
    with open('/data/model/model.json', 'r') as f:
        about = About.parse_obj(json.load(f))
        logging.info(f'Using {about}')

    # NOTE environment var HOST is expected to not contain the protocol
    os.environ['HOST'] = about.host.replace('https://', '').replace('http://', '')
    os.environ['ORGANIZATION'] = about.organization
    os.environ['PROJECT'] = about.project

    if os.path.isfile('/data/model/model.rt'):
        return about

    # NOTE after setting the apropirate env variables we can import loop
    from learning_loop_node import loop

    models = loop.get_json('/models')['models']
    model = [m for m in models if m['version'] == about.version][0]
    logging.info(f'downloading model version {model["version"]}')
    data = loop.get_data(f'/models/{model["id"]}/tensorrt/file')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall('/data/model/')

    logging.info(f'saved model')
    return about
