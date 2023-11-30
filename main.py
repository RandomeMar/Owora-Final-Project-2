from logic import *


def main():
    application = QApplication([])
    window = Logic()
    window.setGeometry(0,0,500,500)
    window.show()
    application.exec()


if __name__ == '__main__':
    main()