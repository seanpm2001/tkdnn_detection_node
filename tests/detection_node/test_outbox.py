
from detector.outbox import Outbox
from PIL import Image
import os


def test_files_are_deleted_after_sending(outbox: Outbox):
    os.mkdir(f'{outbox.path}/test')
    with open(f'{outbox.path}/test/image.json', 'w') as f:
        f.write('{"box_detections":[]}')
        f.close()

    img = Image.new('RGB', (60, 30), color=(73, 109, 137))
    img.save(f'{outbox.path}/test/image.jpg')

    items = outbox.get_data_files()
    assert len(items) == 1

    outbox.upload()
    items = outbox.get_data_files()
    assert len(items) == 0
