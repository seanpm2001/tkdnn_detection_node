
from detector.outbox import Outbox


def test_files_are_deleted_after_sending(outbox: Outbox):
    with open(f'{outbox.path}/test.json', 'w') as f:
        f.write('Json testfile')
        f.close()

    with open(f'{outbox.path}/test.jpg', 'w') as f:
        f.write('Jpg testfile')
        f.close()

    saved_files = outbox.get_data_files()
    assert len(saved_files) == 2

    outbox.submit()

    saved_files = outbox.get_data_files()
    assert len(saved_files) == 0
