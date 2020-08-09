# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WlcOwa
                                 A QGIS plugin
 This plugin calculates WLC or OWA scores for MCDA
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-07-17
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Gregory Huang
        email                : gregory.huang@ryerson.ca
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.gui import *
from qgis.core import *
from qgis.utils import *



# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .wlc_owa_tool_dialog import WlcOwaDialog
import os.path


class WlcOwa:
    """QGIS Plugin Implementation."""

    

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'WlcOwa_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&WLC/OWA Tool')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    def updateCriteria(self):
        """Reload the available fields when layer is changed
        """

        self.dlg.selectCriteria.clear()
        self.dlg.criteriaTable.clear()
        self.dlg.orderTable.clear()
        self.dlg.selectCriteria.addItems([str(x.name()) for x in
            self.dlg.inputBox.currentLayer().fields() if x.isNumeric()])

    # After "Add selected criteria" pushed, or criteria preset changed
    def populateTables(self):
        selected_criteria = self.dlg.selectCriteria.selectedItems()
        flags = Qt.ItemIsEnabled
        if len(selected_criteria) > 0:
            self.dlg.criteriaTable.clearContents()
            self.dlg.criteriaTable.setRowCount(len(selected_criteria))
            self.dlg.orderTable.setRowCount(len(selected_criteria))
            eqWts = round(1/self.dlg.criteriaTable.rowCount(),2)
            for current, i in enumerate(selected_criteria):
                new_criteria = QTableWidgetItem(str(i.text()))
                new_criteria.setFlags(flags)
                self.dlg.criteriaTable.setItem(current, 0, new_criteria)
                if self.dlg.equalWeightBtn.isChecked():
                    self.dlg.criteriaTable.setItem(current, 1, QTableWidgetItem(str(eqWts)))

    # Populate criteria table given preset conditions
    def criteriaPreset(self):
        rows = self.dlg.criteriaTable.rowCount()
        eqWts_btn = round(1/rows,2)
        if self.dlg.equalWeightBtn.isChecked():
            for x in range(rows):
                self.dlg.criteriaTable.setItem(x, 1, QTableWidgetItem(str(eqWts_btn)))

        self.dlg.criteriaTable.clearSelection()

    # Populate order table given preset selections
    def orderPreset(self):
        self.dlg.orderTable.clearContents()
        order_rows = self.dlg.orderTable.rowCount()
        wlcWts = round(1/order_rows,2)
        if self.dlg.wlcBtn.isChecked():
            for x in range(order_rows):
                self.dlg.orderTable.setItem(x, 0, QTableWidgetItem(str(wlcWts)))

        if self.dlg.maxBtn.isChecked():
            self.dlg.orderTable.setItem(0,0, QTableWidgetItem(str("1")))
            for x in range(1,order_rows):
                self.dlg.orderTable.setItem(x, 0, QTableWidgetItem(str("0")))

        if self.dlg.minBtn.isChecked():
            self.dlg.orderTable.setItem(order_rows-1, 0, QTableWidgetItem(str("1")))
            for x in range(0,order_rows-1):
                self.dlg.orderTable.setItem(x, 0, QTableWidgetItem(str("0")))

        if self.dlg.clearOrdBtn.isChecked():
            self.dlg.orderTable.clearContents()

        self.dlg.orderTable.clearSelection()


    # Check if user input is correct
    def checker(self):
        weight_checker = 0
        order_checker = 0

        for row in range(self.dlg.criteriaTable.rowCount()):
            weight_checker += float(self.dlg.criteriaTable.item(row,1).text())
            order_checker += float(self.dlg.orderTable.item(row,0).text())

        if weight_checker == 1:
            pass
        else:
            iface.messageBar().pushMessage("Input error", 
                "Criteria Weights need to sum to 1",
                level = Qgis.Critical,
                duration = 10)
            return False

        if order_checker == 1:
            pass
        else:
            iface.messageBar().pushMessage("Input error",
                "Order Weights need to sum to 1",
                level = Qgis.Critical,
                duration = 10)
            return False

        return True


    # Calculate OWA score
    def calculateOWA(self):

        layer = self.dlg.inputBox.currentLayer()
        pr = layer.dataProvider()
        pr.addAttributes([QgsField('OWA Score', QVariant.Double, len=7, prec=5)])
        layer.updateFields()
        fld_index = layer.fields().lookupField('OWA Score')
        criteria_cols = self.dlg.criteriaTable.columnCount()
        criteria_rows = self.dlg.criteriaTable.rowCount()

        for location in layer.getFeatures():
            attribute_map = {}
            value_times_weight = []
            order_weight = []
            for row in range(criteria_rows):
                atts = []
                order_item = self.dlg.orderTable.item(row,0).text()
                order_weight.append(order_item)
                for col in range(criteria_cols):
                    tbl_item = self.dlg.criteriaTable.item(row,col).text()
                    atts.append(tbl_item)
                result = location[atts[0]]*float(atts[1])
                value_times_weight.append(result)

            value_times_weight.sort(reverse = True)
            order_applied = []
            for x in range(len(value_times_weight)):
                    order_applied.append(value_times_weight[x]*float(order_weight[x]))

            owa_score = sum(order_applied)
            atts = {}
            atts[fld_index] = owa_score
            attribute_map[location.id()] = atts
            with edit(layer):
                pr.changeAttributeValues(attribute_map)



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('WlcOwa', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/wlc_owa_tool/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Calculate WLC or OWA'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&WLC/OWA Tool'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = WlcOwaDialog()

        # show the dialog
        self.dlg.show()

        # Run the dialog event loop

        # Setup and link widgets
        # Reload available fields when layer is changed by calling 
        # updateCriteria function
        self.dlg.inputBox.layerChanged.connect(self.updateCriteria)
        # Populate criteria selection table once layer is selected
        # Make sure available options are all numeric
        self.dlg.selectCriteria.addItems([str(x.name()) for x in
            self.dlg.inputBox.currentLayer().fields() if x.isNumeric()])

        # Allow multiple selection in the select criteria box
        self.dlg.selectCriteria.setSelectionMode(QAbstractItemView.MultiSelection)

        # Populate the tables after criteria are selected (button clicked)
        self.dlg.addCriteria.clicked.connect(self.populateTables)

        # Populate the criteria weights if preset is clicked
        self.dlg.equalWeightBtn.toggled.connect(self.criteriaPreset)

        # Repopulate the criteria table now that criteria weights are manual
        self.dlg.clearWtsBtn.clicked.connect(self.populateTables)

        # Action for order weights table
        self.dlg.maxBtn.clicked.connect(self.orderPreset)
        self.dlg.minBtn.clicked.connect(self.orderPreset)
        self.dlg.wlcBtn.clicked.connect(self.orderPreset)
        self.dlg.clearOrdBtn.clicked.connect(self.orderPreset)

        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            
            # Check if criteria and order weights are correct (sum to 1)
            if self.checker() == True:
                self.calculateOWA()
                iface.messageBar().pushMessage("Success",
                    "OWA Score calculated",
                    level = Qgis.Success,
                    duration = 10)

            pass
