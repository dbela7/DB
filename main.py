import sys
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from app.bootstrap import bootstrap_app


def excepthook(exctype, value, tb):
    msg = "".join(traceback.format_exception(exctype, value, tb))
    print(msg)
    QMessageBox.critical(None, "Program hiba", msg)


def main():
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    w = bootstrap_app()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
