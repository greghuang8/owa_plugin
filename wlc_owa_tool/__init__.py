# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WlcOwa
                                 A QGIS plugin
 This plugin calculates WLC or OWA scores for MCDA
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-08-05
        copyright            : (C) 2020 by Gregory Huang
        email                : gregory.huang@ryerson.ca
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load WlcOwa class from file WlcOwa.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .wlc_owa_tool import WlcOwa
    return WlcOwa(iface)