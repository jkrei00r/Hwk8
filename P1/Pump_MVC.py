# region imports
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import PyQt5.QtWidgets as qtw
from LeastSquares import LeastSquaresFit_Class


# endregion

# region class definitions
class Pump_Model():
    """This is the pump model. It just stores data."""

    def __init__(self):
        # Create class variables for storing information
        self.PumpName = ""
        self.FlowUnits = ""
        self.HeadUnits = ""

        # Place to store data from file
        self.FlowData = np.array([])
        self.HeadData = np.array([])
        self.EffData = np.array([])

        # Place to store coefficients for fits
        self.HeadCoefficients = np.array([])
        self.EfficiencyCoefficients = np.array([])

        # Create instances of least squares class
        self.LSFitHead = LeastSquaresFit_Class()
        self.LSFitEff = LeastSquaresFit_Class()


class Pump_Controller():
    def __init__(self):
        self.Model = Pump_Model()
        self.View = Pump_View()

    def ImportFromFile(self, data):
        """Processes the list of strings in data to build the pump model"""
        if len(data) < 3:
            raise ValueError("File must contain at least 3 lines")

        self.Model.PumpName = data[0].strip()

        # Process units line
        units = data[1].split()
        if len(units) < 2:
            raise ValueError("Units line must contain at least 2 values")
        self.Model.FlowUnits = units[0].strip()
        self.Model.HeadUnits = units[1].strip()

        # Extract and process data
        self.SetData(data[2:])
        self.updateView()

    def SetData(self, data):
        """Parse data lines and build arrays"""
        # Clear existing data
        self.Model.FlowData = np.array([])
        self.Model.HeadData = np.array([])
        self.Model.EffData = np.array([])

        # Parse new data
        for line in data:
            cells = line.split()
            if len(cells) < 3:
                continue  # Skip incomplete lines

            try:
                self.Model.FlowData = np.append(self.Model.FlowData, float(cells[0].strip()))
                self.Model.HeadData = np.append(self.Model.HeadData, float(cells[1].strip()))
                self.Model.EffData = np.append(self.Model.EffData, float(cells[2].strip()))
            except ValueError as e:
                print(f"Skipping line due to error: {str(e)}")
                continue

        # Perform curve fitting
        self.LSFit()

    def LSFit(self):
        """Perform least squares fitting"""
        if len(self.Model.FlowData) == 0:
            return

        # Quadratic fit for head (degree=2)
        self.Model.LSFitHead.x = self.Model.FlowData
        self.Model.LSFitHead.y = self.Model.HeadData
        self.Model.HeadCoefficients = self.Model.LSFitHead.LeastSquares(2)

        # Cubic fit for efficiency (degree=3)
        self.Model.LSFitEff.x = self.Model.FlowData
        self.Model.LSFitEff.y = self.Model.EffData
        self.Model.EfficiencyCoefficients = self.Model.LSFitEff.LeastSquares(3)

    def setViewWidgets(self, w):
        self.View.setViewWidgets(w)

    def updateView(self):
        self.View.updateView(self.Model)


class Pump_View():
    def __init__(self):
        """Initialize view components"""
        self.LE_PumpName = qtw.QLineEdit()
        self.LE_FlowUnits = qtw.QLineEdit()
        self.LE_HeadUnits = qtw.QLineEdit()
        self.LE_HeadCoefs = qtw.QLineEdit()
        self.LE_EffCoefs = qtw.QLineEdit()
        self.ax = None
        self.canvas = None

    def updateView(self, Model):
        """Update all view components with model data"""
        self.LE_PumpName.setText(Model.PumpName)
        self.LE_FlowUnits.setText(Model.FlowUnits)
        self.LE_HeadUnits.setText(Model.HeadUnits)
        self.LE_HeadCoefs.setText(Model.LSFitHead.GetCoeffsString())
        self.LE_EffCoefs.setText(Model.LSFitEff.GetCoeffsString())
        self.DoPlot(Model)

    def DoPlot(self, Model):
        """Create the performance plot"""
        if len(Model.FlowData) == 0:
            return

        # Get fit data
        headx, heady, headRSq = Model.LSFitHead.GetPlotInfo(2, npoints=500)
        effx, effy, effRSq = Model.LSFitEff.GetPlotInfo(3, npoints=500)

        # Clear previous plot
        self.ax.clear()

        # Plot head data and fit
        self.ax.plot(Model.FlowData, Model.HeadData, 'bo', label='Head Data')
        self.ax.plot(headx, heady, 'b-', label=f'Head Fit (R²={headRSq:.3f})')
        self.ax.set_xlabel(f'Flow Rate ({Model.FlowUnits})')
        self.ax.set_ylabel(f'Head ({Model.HeadUnits})', color='b')
        self.ax.tick_params(axis='y', labelcolor='b')

        # Create second y-axis for efficiency
        ax2 = self.ax.twinx()
        ax2.plot(Model.FlowData, Model.EffData, 'ro', label='Efficiency Data')
        ax2.plot(effx, effy, 'r-', label=f'Efficiency Fit (R²={effRSq:.3f})')
        ax2.set_ylabel('Efficiency (%)', color='r')
        ax2.tick_params(axis='y', labelcolor='r')

        # Set title and legend
        self.ax.set_title(f'Pump Performance: {Model.PumpName}')
        lines, labels = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.ax.legend(lines + lines2, labels + labels2, loc='upper right')

        # Refresh canvas
        self.canvas.draw_idle()

    def setViewWidgets(self, w):
        self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits, \
            self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas = w
# endregion
