import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from stl import mesh
import numpy as np



UI_FOLDER = "uis"
MAIN_WINDOW_FILENAME = "main.ui"
MAIN_WINDOW_PATH = os.path.join(UI_FOLDER, MAIN_WINDOW_FILENAME)

class Viewer(gl.GLViewWidget):
    def __init__(self):
        super(Viewer, self).__init__()

        #remove
        self.currentSTL = None

        self.setWindowTitle('Your Protein')
        self.distance = 40
        self.setCameraPosition(distance=40)

        g = gl.GLGridItem()
        g.setSize(200, 200)
        g.setSpacing(5, 5)
        self.addItem(g)

        self.noRepeatKeys.extend([QtCore.Qt.Key.Key_D,
                                  QtCore.Qt.Key.Key_A,
                                  QtCore.Qt.Key.Key_W,
                                  QtCore.Qt.Key.Key_S,
                                  QtCore.Qt.Key.Key_Q,
                                  QtCore.Qt.Key.Key_E])

    def evalKeyState(self):
        speed = 2.0
        zoom_speed = 4.0
        if len(self.keysPressed) > 0:
            if QtCore.Qt.Key.Key_E in self.keysPressed and QtCore.Qt.Key.Key_Q in self.keysPressed:
                del self.keysPressed[QtCore.Qt.Key.Key_E]
                del self.keysPressed[QtCore.Qt.Key.Key_Q]

            for key in self.keysPressed:
                if key == QtCore.Qt.Key.Key_Right or key == QtCore.Qt.Key.Key_D:
                    self.orbit(azim=-speed, elev=0)
                elif key == QtCore.Qt.Key.Key_Left or key == QtCore.Qt.Key.Key_A:
                    self.orbit(azim=speed, elev=0)
                elif key == QtCore.Qt.Key.Key_Up or key == QtCore.Qt.Key.Key_W:
                    self.orbit(azim=0, elev=-speed)
                elif key == QtCore.Qt.Key.Key_Down or key == QtCore.Qt.Key.Key_S:
                    self.orbit(azim=0, elev=speed)
                elif key == QtCore.Qt.Key.Key_Q:
                    self.opts['fov'] *= 0.999 ** zoom_speed
                    self.update()
                elif key == QtCore.Qt.Key.Key_E:
                    self.opts['distance'] *= 0.999 ** -zoom_speed
                    self.update()

                self.keyTimer.start(16)
        else:
            self.keyTimer.stop()


    def mouseMoveEvent(self, ev):
        #lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        lpos = ev.localPos()
        if not hasattr(self, 'mousePos'):
            self.mousePos = lpos
        diff = lpos - self.mousePos
        self.mousePos = lpos

        if ev.buttons() == QtCore.Qt.MouseButton.LeftButton:
            if (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
                self.pan(diff.x(), diff.y(), 0, relative='view')
            else:
                self.orbit(-diff.x(), diff.y())
        elif ev.buttons() == QtCore.Qt.MouseButton.MiddleButton:
            if (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier):
                self.pan(diff.x(), 0, diff.y(), relative='view-upright')
            else:
                self.pan(diff.x(), diff.y(), 0, relative='view-upright')


    def showSTL(self, filename):
        if self.currentSTL:
            self.removeItem(self.currentSTL)

        points, faces = self.loadSTL(filename)
        meshdata = gl.MeshData(vertexes=points, faces=faces)
        mesh = gl.GLMeshItem(meshdata=meshdata, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))
        self.addItem(mesh)

        self.currentSTL = mesh

    def loadSTL(self, filename):
        m = mesh.Mesh.from_file(filename)
        shape = m.points.shape
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(MAIN_WINDOW_PATH, self)

        self.setWindowTitle("Protein3D")

        self.viewer_layout = self.findChild(QtWidgets.QVBoxLayout, "viewerLayout")
        self.viewer = Viewer()
        self.viewer_layout.addWidget(self.viewer, 1)

        self.file_path = None
        self.open_file_button = self.findChild(QtWidgets.QAction, "OpenPDBFile")
        self.open_file_button.triggered.connect(self.open_file)

        self.show()

    def open_file(self):
        #file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        #    self, "Открыть файл", ".", "PDB File (*.pdb *.pdb1)"
        #)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Открыть файл", ".", "STL File (*.stl *.STL)"
        )
        self.viewer.showSTL(file_path)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()