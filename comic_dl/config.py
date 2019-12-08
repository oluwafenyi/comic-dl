import os


DB_PATH = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'assets'
        )

BASE_PATH = os.path.dirname(os.path.dirname(__file__))

TEMP_PATH = os.path.join(BASE_PATH, 'temp')

ARCHIVE_PATH = os.path.join(BASE_PATH, 'archives')
