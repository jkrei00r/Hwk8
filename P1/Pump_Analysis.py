# region imports
import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from Pump_MVC import Pump_Controller
from pump import Ui_Form


# endregion

class MainWindow(qtw.QWidget, Ui_Form):
    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        print("Initializing MainWindow...")

        # Setup UI
        self.setupUi(self)
        print("UI setup complete")

        # Create controller
        self.controller = Pump_Controller()
        print("Controller created")

        # Setup matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 8), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        print("Matplotlib figure created")

        # Setup plot widget
        if self.W_Plot.layout():
            qtc.QObjectCleanupHandler().add(self.W_Plot.layout())
        plot_layout = qtw.QVBoxLayout(self.W_Plot)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(self.canvas)
        print("Plot widget setup complete")

        # Connect view widgets to controller
        self.controller.setViewWidgets([
            self.LE_PumpName,
            self.LE_FlowUnits,
            self.LE_HeadUnits,
            self.LE_HeadCoefs,
            self.LE_EffCoefs,
            self.ax,
            self.canvas
        ])
        print("View widgets connected")

        # Connect signals
        self.CMD_Open.clicked.connect(self.openFile)
        self.PB_Exit.clicked.connect(self.close)
        print("Signals connected")

        # Initialize last directory
        self.lastDirectory = ""

        # Show window
        self.show()
        print(f"Window visible: {self.isVisible()}")
        print("MainWindow initialization complete")

    def openFile(self):
        """Open a file dialog to select a pump data file"""
        print("Opening file dialog...")
        filename, _ = qtw.QFileDialog.getOpenFileName(
            self,
            "Open Pump Data File",
            self.lastDirectory,
            "Text Files (*.txt);;All Files (*)"
        )

        if filename:
            print(f"Selected file: {filename}")
            self.lastDirectory = filename
            self.TE_Filename.setText(filename)

            try:
                with open(filename, 'r') as f:
                    data = f.readlines()
                print(f"Read {len(data)} lines from file")
                self.controller.ImportFromFile(data)
                print("Data imported successfully")
            except Exception as e:
                print(f"Error loading file: {str(e)}")
                qtw.QMessageBox.critical(self, "Error", f"Could not load file:\n{str(e)}")


if __name__ == '__main__':
    print("Starting application...")
    app = qtw.QApplication(sys.argv)
    print("QApplication created")

    mw = MainWindow()
    mw.setWindowTitle('Pump Performance Analyzer')
    print("MainWindow created and shown")

    print("Starting event loop")
    sys.exit(app.exec())