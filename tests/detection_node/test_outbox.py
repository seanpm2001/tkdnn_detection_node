
from detector.outbox import Outbox
from PIL import Image


def test_files_are_deleted_after_sending(outbox: Outbox):
    with open(f'{outbox.path}/test.json', 'w') as f:
        f.write('{"box_detections":[]}')
        f.close()

    img = Image.new('RGB', (60, 30), color=(73, 109, 137))
    img.save(f'{outbox.path}/test.jpg')

    saved_files = outbox.get_data_files()
    assert len(saved_files) == 2

    outbox.submit()

    saved_files = outbox.get_data_files()
    assert len(saved_files) == 0
