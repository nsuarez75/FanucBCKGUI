
from asyncio.windows_events import NULL
from importlib.resources import path
from multiprocessing.pool import ThreadPool
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, pyqtSlot, QThreadPool
from ftplib import FTP
import os
from time import sleep
from unittest import skip
import pickle
from datetime import datetime
import logging


class Fanuc():

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

    def guardar_pickle(self, obj):  # guardar pickle
        try:
            with open("robots.pickle", "wb") as f:
                pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as ex:
            print("Error during pickling object (Possibly unsupported):", ex)

    def leer_pickle(self):  # leer pickle
        try:
            with open("robots.pickle", "rb") as f:
                return pickle.load(f)
        except Exception as ex:
            print("Error during unpickling object (Possibly unsupported):", ex)

    def borrar_robot(self, nombre):  # borra robot del pickle
        if os.path.exists("robots.pickle"):
            print("---------------------------------")
            robots = self.leer_pickle()
            for robot in robots:
                if robot['nombre'] == nombre:
                    robots.remove(robot)
                    break
            self.guardar_pickle(robots)

    def añadir_robot(self, nuevo_robot):  # añadir robot al pickle
        if os.path.exists("robots.pickle"):
            robots = self.leer_pickle()
            robots.append(nuevo_robot)
            self.guardar_pickle(robots)
        else:
            self.guardar_pickle([nuevo_robot])


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit()


class Ui_MainWindow(object):

    fanuc = Fanuc()
    threadpool = QThreadPool()
    proceso = 0
    proceso_total = 0
    carpeta_raiz = ""
    carpeta_objetivo = ""

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(524, 244)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listaRobots = QtWidgets.QListWidget(self.centralwidget)
        self.listaRobots.setSelectionMode(QtWidgets.QListWidget.MultiSelection)
        self.listaRobots.setGeometry(QtCore.QRect(260, 11, 256, 191))
        self.listaRobots.setObjectName("listaRobots")
        self.botonAgregar = QtWidgets.QPushButton(self.centralwidget)
        self.botonAgregar.setGeometry(QtCore.QRect(190, 10, 61, 31))
        self.botonAgregar.setObjectName("botonAgregar")
        self.botonBorrar = QtWidgets.QPushButton(self.centralwidget)
        self.botonBorrar.setGeometry(QtCore.QRect(190, 50, 61, 31))
        self.botonBorrar.setObjectName("botonBorrar")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 51, 16))
        self.label.setObjectName("etiquetanombre")
        self.nombreIn = QtWidgets.QLineEdit(self.centralwidget)
        self.nombreIn.setGeometry(QtCore.QRect(10, 30, 113, 21))
        self.nombreIn.setObjectName("nombreIn")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 49, 16))
        self.label_2.setObjectName("etiquetagrupo")
        self.grupoIn = QtWidgets.QLineEdit(self.centralwidget)
        self.grupoIn.setGeometry(QtCore.QRect(10, 76, 113, 21))
        self.grupoIn.setObjectName("grupoIn")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 100, 49, 16))
        self.label_3.setObjectName("etiquetaip")
        self.ipIn = QtWidgets.QLineEdit(self.centralwidget)
        self.ipIn.setGeometry(QtCore.QRect(10, 120, 113, 21))
        self.ipIn.setObjectName("ipIn")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10, 150, 49, 16))
        self.label_4.setObjectName("etiquetaip")
        self.ruta = QtWidgets.QLineEdit(self.centralwidget)
        self.ruta.setGeometry(QtCore.QRect(10, 170, 160, 21))
        self.ruta.setObjectName("rutain")
        self.botonBackup = QtWidgets.QPushButton(self.centralwidget)
        self.botonBackup.setGeometry(QtCore.QRect(190, 90, 61, 31))
        self.botonBackup.setObjectName("botonbackup")
        self.botondirectorio = QtWidgets.QPushButton(self.centralwidget)
        self.botondirectorio.setGeometry(QtCore.QRect(190, 130, 61, 31))
        self.botondirectorio.setObjectName("botondirectorio")
        self.gruposRobots = QtWidgets.QComboBox(self.centralwidget)
        self.gruposRobots.setGeometry(QtCore.QRect(190, 180, 68, 22))
        self.gruposRobots.setObjectName("gruposRobots")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(20, 210, 481, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.hide()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # botones
        self.botonAgregar.clicked.connect(lambda: self.añadir_robot())
        self.botonBorrar.clicked.connect(lambda: self.borrar_robot())
        self.botonBackup.clicked.connect(lambda: self.multi_backup())
        self.botondirectorio.clicked.connect(lambda: self.leer_directorio())

        # eventos
        self.gruposRobots.currentIndexChanged.connect(
            lambda: self.actualizar_lista())

        # cargar pickle
        self.actualizar_grupos()
        self.actualizar_lista()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            "MainWindow", "Auto Backup Fanuc"))
        self.botonAgregar.setText(_translate("MainWindow", "AGREGAR"))
        self.botonBorrar.setText(_translate("MainWindow", "BORRAR"))
        self.label.setText(_translate("MainWindow", "Nombre:"))
        self.label_2.setText(_translate("MainWindow", "Grupo:"))
        self.label_3.setText(_translate("MainWindow", "IP:"))
        self.label_4.setText(_translate("MainWindow", "Ruta:"))
        self.botonBackup.setText(_translate("MainWindow", "BACKUP"))
        self.botondirectorio.setText(_translate("MainWindow", "RUTA"))

    def añadir_robot(self):
        if (self.nombreIn.text() != "" and self.grupoIn.text() != "" and self.ipIn.text() != ""):
            robot = {"nombre": self.nombreIn.text(
            ), "plc": self.grupoIn.text(), "ip": self.ipIn.text()}
            self.fanuc.añadir_robot(robot)
            self.actualizar_grupos()

    def borrar_robot(self):
        seleccion = self.listaRobots.selectedItems()
        nombres = []
        for nombre in seleccion:
            nombres.append(nombre.text())
            print(nombre)

        for robot in self.fanuc.leer_pickle():
            print(self.gruposRobots.currentText())
            if (robot["plc"] == self.gruposRobots.currentText() and robot["nombre"] in nombres):
                self.fanuc.borrar_robot(robot["nombre"])
                nombres.remove(robot["nombre"])

        self.actualizar_grupos()
        self.actualizar_lista()

    def actualizar_lista(self):
        self.listaRobots.clear()
        robots = []
        if self.gruposRobots.currentText() != "":
            for robot in self.fanuc.leer_pickle():
                if (robot["nombre"] not in robots and robot["plc"] == self.gruposRobots.currentText()):
                    robots.append(robot["nombre"])
            self.listaRobots.addItems(robots)

    def actualizar_grupos(self):
        try:
            self.gruposRobots.clear()
            grupos = []
            for grupo in self.fanuc.leer_pickle():
                if grupo['plc'] not in grupos:
                    grupos.append(grupo['plc'])
            self.gruposRobots.addItems(grupos)

        except:
            pass

    def ftp_getfiles_multi(self, path, robot):  # recibir archivos por ftp

        try:

            # print(f"Conectandose a {robot['nombre']}")
            ftp = FTP(robot['ip'])
            ftp.login()
            os.mkdir(path)
            archivos = ftp.nlst()
            # print(f"{robot['nombre']} conectado!")
            cantidad = 0
            for archivo in archivos:
                cantidad += 1

            for archivo in archivos:
                with open(path + "\\" + archivo, "wb") as file:
                    ftp.retrbinary(f"RETR {archivo}", file.write)

            ftp.close()
            ftp = None
            # print(f"Backup {robot['nombre']} completado!")

        except Exception as e:
            robotfallo = f"{self.carpeta_raiz}\\error.log"
            logging.basicConfig(filename=robotfallo,
                                level=logging.ERROR, filemode="w")
            logging.error(f"Error haciendo backup de {robot['nombre']}")

    def multi_backup(self):
        robots = self.fanuc.leer_pickle()
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y_%H%M")
        self.carpeta_raiz = f"{self.carpeta_objetivo}\\Backup_{self.gruposRobots.currentText()}_{dt_string}"

        seleccion = []
        for item in self.listaRobots.selectedItems():
            seleccion.append(item.text())

        workers = []
        for robot in robots:
            if (robot['plc'] == self.gruposRobots.currentText() and robot['nombre'] in seleccion):
                carpeta_robot = f"{self.carpeta_raiz}\\{robot['nombre']}"

                worker = Worker(
                    self.ftp_getfiles_multi, carpeta_robot, robot)

                worker.signals.finished.connect(self.thread_complete)
                workers.append(worker)
                self.proceso_total += 1

        self.progressBar.show()
        self.progressBar.setMaximum(self.proceso_total)
        self.botonBackup.hide()
        self.botonAgregar.hide()
        self.botonBorrar.hide()
        self.gruposRobots.hide()
        self.botondirectorio.hide()

        if workers != []:
            os.mkdir(self.carpeta_raiz)
            for worker in workers:
                self.threadpool.start(worker)

    def thread_complete(self):
        self.proceso += 1
        self.progressBar.setValue(self.proceso)
        if self.proceso == self.proceso_total:
            self.progressBar.hide()
            self.botonBackup.show()
            self.botonAgregar.show()
            self.botonBorrar.show()
            self.gruposRobots.show()
            self.botondirectorio.show()

    def leer_directorio(self):
        ruta = QtWidgets.QFileDialog.getExistingDirectory(
            caption='Seleccionar path'
        )
        self.ruta.setText(ruta)
        self.carpeta_objetivo = ruta


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.setWindowIcon(QtGui.QIcon("./Baie_r30ibplus.ico"))
    MainWindow.show()
    sys.exit(app.exec_())
