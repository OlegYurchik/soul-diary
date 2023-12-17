import pathlib
import sys

current_path = str(pathlib.Path(__file__).parent.absolute())
if current_path not in sys.path:
    sys.path.append(current_path)

import flet

from app.app import SoulDiaryApp


if __name__ == "__main__":
    flet.app(target=SoulDiaryApp().run)
