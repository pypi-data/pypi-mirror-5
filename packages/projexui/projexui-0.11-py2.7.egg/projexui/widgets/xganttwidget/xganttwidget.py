#!/usr/bin/python

""" Defines a gantt chart widget for use in scheduling applications. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

from projexui.qt import Signal
from projexui.qt.QtCore   import QDate,\
                                 Qt,\
                                 QSize

from projexui.qt.QtGui    import QWidget,\
                                 QPen,\
                                 QBrush,\
                                 QPalette,\
                                 QColor

from projex.enum import enum

import projexui

from projexui.widgets.xganttwidget.xganttscene   import XGanttScene

class XGanttWidget(QWidget):
    dateRangeChanged = Signal()
    
    Timescale = enum('Week', 'Month', 'Year')
    
    def __init__( self, parent = None ):
        super(XGanttWidget, self).__init__( parent )
        
        # load the user interface
        projexui.loadUi(__file__, self)
        
        # define custom properties
        self._backend               = None
        self._dateStart             = QDate.currentDate().addMonths(-2)
        self._dateEnd               = QDate.currentDate().addMonths(2)
        self._alternatingRowColors  = False
        self._cellWidth             = 20
        self._cellHeight            = 20
        self._first                 = True
        self._dateFormat            = 'M/d/yy'
        self._timescale             = XGanttWidget.Timescale.Month
        self._scrolling             = False
        
        # setup the palette colors
        palette = self.palette()
        color   = palette.color(palette.Base)
        
        self._gridPen           = QPen(color.darker(115))
        self._brush             = QBrush(color)
        self._alternateBrush    = QBrush(color.darker(105))
        
        weekendColor            = color.darker(108)
        self._weekendBrush      = QBrush(weekendColor)
        
        # setup the columns for the tree
        self.setColumns(['Name', 'Start', 'End', 'Duration'])
        header = self.uiGanttTREE.header()
        header.setFixedHeight(self._cellHeight * 2)
        headerItem = self.uiGanttTREE.headerItem()
        headerItem.setSizeHint(0, QSize(80, header.height()))
        
        # initialize the tree widget
        self.uiGanttTREE.setShowGrid(False)
        self.uiGanttTREE.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.uiGanttTREE.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.uiGanttTREE.setVerticalScrollMode(self.uiGanttTREE.ScrollPerPixel)
        
        # initialize the view widget
        self.uiGanttVIEW.setDragMode( self.uiGanttVIEW.RubberBandDrag )
        self.uiGanttVIEW.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.uiGanttVIEW.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.uiGanttVIEW.setScene(XGanttScene(self))
        self.uiGanttVIEW.installEventFilter(self)
        
        # create connections
        self.uiGanttTREE.itemExpanded.connect(self.syncView)
        self.uiGanttTREE.itemCollapsed.connect(self.syncView)
        
        # connect scrollbars
        tree_bar = self.uiGanttTREE.verticalScrollBar()
        view_bar = self.uiGanttVIEW.verticalScrollBar()
        
        tree_bar.rangeChanged.connect(self.__updateViewRect)
        tree_bar.valueChanged.connect(self.__scrollView)
        view_bar.valueChanged.connect(self.__scrollTree)
        
        # connect selection
        self.uiGanttTREE.itemSelectionChanged.connect(self.__selectView)
        self.uiGanttVIEW.scene().selectionChanged.connect(self.__selectTree)
    
    def __scrollTree( self, value ):
        """
        Updates the tree view scrolling to the inputed value.
        
        :param      value | <int>
        """
        if ( self._scrolling ):
            return
        
        tree_bar = self.uiGanttTREE.verticalScrollBar()
        self._scrolling = True
        tree_bar.setValue(value)
        self._scrolling = False
        
    def __scrollView( self, value ):
        """
        Updates the gantt view scrolling to the inputed value.
        
        :param      value | <int>
        """
        if ( self._scrolling ):
            return
        
        view_bar = self.uiGanttVIEW.verticalScrollBar()
        self._scrolling = True
        view_bar.setValue(value)
        self._scrolling = False
    
    def __selectTree( self ):
        """
        Matches the tree selection to the views selection.
        """
        self.uiGanttTREE.blockSignals(True)
        self.uiGanttTREE.clearSelection()
        for item in self.uiGanttVIEW.scene().selectedItems():
            item.treeItem().setSelected(True)
        self.uiGanttTREE.blockSignals(False)
    
    def __selectView( self ):
        """
        Matches the view selection to the trees selection.
        """
        self.uiGanttVIEW.scene().blockSignals(True)
        self.uiGanttVIEW.scene().clearSelection()
        for item in self.uiGanttTREE.selectedItems():
            item.viewItem().setSelected(True)
        self.uiGanttVIEW.scene().blockSignals(False)
    
    def __updateViewRect( self ):
        """
        Updates the view rect to match the current tree value.
        """
        header_h    = self._cellHeight * 2
        rect        = self.uiGanttVIEW.scene().sceneRect()
        sbar_max    = self.uiGanttTREE.verticalScrollBar().maximum()
        sbar_max   += self.uiGanttTREE.viewport().height() + header_h
        widget_max  = self.uiGanttVIEW.height()
        widget_max -= (self.uiGanttVIEW.horizontalScrollBar().height() + 10)
        
        rect.setHeight(max(widget_max, sbar_max))
        self.uiGanttVIEW.scene().setSceneRect(rect)
    
    def addTopLevelItem( self, item ):
        """
        Adds the inputed item to the gantt widget.
        
        :param      item | <XGanttWidgetItem>
        """
        self.treeWidget().addTopLevelItem(item)
        self.viewWidget().scene().addItem(item.viewItem())
        
        item.sync(recursive = True)
        
    def alternateBrush( self ):
        """
        Returns the alternate brush to be used for the grid view.
        
        :return     <QBrush>
        """
        return self._alternateBrush
    
    def alternatingRowColors( self ):
        """
        Returns whether or not this widget should show alternating row colors.
        
        :return     <bool>
        """
        return self._alternatingRowColors
    
    def brush( self ):
        """
        Returns the background brush to be used for the grid view.
        
        :return     <QBrush>
        """
        return self._brush
    
    def cellHeight( self ):
        """
        Returns the height for the cells in this gantt's views.
        
        :return     <int>
        """
        return self._cellHeight
    
    def cellWidth( self ):
        """
        Returns the width for the cells in this gantt's views.
        
        :return     <int>
        """
        return self._cellWidth
    
    def clear( self ):
        """
        Clears all the gantt widget items for this widget.
        """
        self.uiGanttTREE.clear()
        self.uiGanttVIEW.scene().clear()
    
    def columns( self ):
        """
        Returns a list of the columns being used in the treewidget of this gantt
        chart.
        
        :return     [<str>, ..]
        """
        return self.treeWidget().columns()
    
    def dateEnd( self ):
        """
        Returns the date end for this date range of this gantt widget.
        
        :return     <QDate>
        """
        return self._dateEnd
    
    def dateFormat( self ):
        """
        Returns the date format that will be used when rendering items in the
        view.
        
        :return     <str>
        """
        return self._dateFormat
    
    def dateStart( self ):
        """
        Returns the date start for the date range of this gantt widget.
        
        :return     <QDate>
        """
        return self._dateStart
    
    def emitDateRangeChanged( self ):
        """
        Emits the date range changed signal provided signals aren't being
        blocked.
        """
        if ( not self.signalsBlocked() ):
            self.dateRangeChanged.emit()
    
    def eventFilter( self, object, event ):
        if ( event.type() == event.Resize ):
            self.__updateViewRect()
        return False
    
    def gridPen( self ):
        """
        Returns the pen that this widget uses to draw in the view.
        
        :return     <QPen>
        """
        return self._gridPen
    
    def indexOfTopLevelItem( self, item ):
        """
        Returns the index for the inputed item from the tree.
        
        :return     <int>
        """
        return self.treeWidget().indexOfTopLevelItem(item)
    
    def insertTopLevelItem( self, index, item ):
        """
        Inserts the inputed item at the given index in the tree.
        
        :param      index   | <int>
                    item    | <XGanttWidgetItem>
        """
        self.treeWidget().insertTopLevelItem(index, item)
        
        item.sync(recursive = True)
    
    def setAlternateBrush( self, brush ):
        """
        Sets the alternating brush used for this widget to the inputed brush.
        
        :param      brush | <QBrush> || <QColor>
        """
        self._alternateBrush = QBrush(brush)
    
    def setAlternatingRowColors( self, state ):
        """
        Sets the alternating row colors state for this widget.
        
        :param      state | <bool>
        """
        self._alternatingRowColors = state
        
        self.treeWidget().setAlternatingRowColors(state)
    
    def setBrush( self, brush ):
        """
        Sets the main background brush used for this widget to the inputed
        brush.
        
        :param      brush | <QBrush> || <QColor>
        """
        self._brush = QBrush(brush)
    
    def setCellHeight( self, cellHeight ):
        """
        Sets the height for the cells in this gantt's views.
        
        :param      cellHeight | <int>
        """
        self._cellHeight = cellHeight
    
    def setCellWidth( self, cellWidth ):
        """
        Sets the width for the cells in this gantt's views.
        
        :param      cellWidth | <int>
        """
        self._cellWidth = cellWidth
    
    def setColumns( self, columns ):
        """
        Sets the columns for this gantt widget's tree to the inputed list of
        columns.
        
        :param      columns | {<str>, ..]
        """
        self.treeWidget().setColumns(columns)
        item = self.treeWidget().headerItem()
        for i in range(item.columnCount()):
            item.setTextAlignment(i, Qt.AlignBottom | Qt.AlignHCenter)
    
    def setDateEnd( self, dateEnd ):
        """
        Sets the end date for the range of this gantt widget.
        
        :param      dateEnd | <QDate>
        """
        self._dateEnd = dateEnd
        self.emitDateRangeChanged()
    
    def setDateFormat( self, format ):
        """
        Sets the date format that will be used when rendering in the views.
        
        :return     <str>
        """
        return self._dateFormat
    
    def setDateStart( self, dateStart ):
        """
        Sets the start date for the range of this gantt widget.
        
        :param      dateStart | <QDate>
        """
        self._dateStart = dateStart
        self.emitDateRangeChanged()
    
    def setGridPen( self, pen ):
        """
        Sets the pen used to draw the grid lines for the view.
        
        :param      pen | <QPen> || <QColor>
        """
        self._gridPen = QPen(pen)
    
    def setTimescale( self, timescale ):
        """
        Sets the timescale value for this widget to the inputed value.
        
        :param      timescale | <XGanttWidget.Timescale>
        """
        self._timescale = timescale
    
    def setWeekendBrush( self, brush ):
        """
        Sets the brush to be used when coloring weekend columns.
        
        :param      brush | <QBrush> || <QColor>
        """
        self._weekendBrush = QBrush(brush)
    
    def syncView( self ):
        """
        Syncs all the items to the view.
        """
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            item.syncView(recursive = True)
    
    def takeTopLevelItem( self, index ):
        """
        Removes the top level item at the inputed index from the widget.
        
        :param      index | <int>
        
        :return     <XGanttWidgetItem> || None
        """
        item = self.topLevelItem(index)
        if ( item ):
            self.viewWidget().scene().removeItem(item.viewItem())
            self.treeWidget().takeTopLevelItem(index)
            
            return item
        return None
    
    def timescale( self ):
        """
        Returns the timescale that is being used for this widget.
        
        :return     <XGanttWidget.Timescale>
        """
        return self._timescale
    
    def topLevelItem( self, index ):
        """
        Returns the top level item at the inputed index.
        
        :return     <XGanttWidgetItem>
        """
        return self.treeWidget().topLevelItem(index)
    
    def topLevelItemCount( self ):
        """
        Returns the number of top level items for this widget.
        
        :return     <int>
        """
        return self.treeWidget().topLevelItemCount()
    
    def treeWidget( self ):
        """
        Returns the tree widget for this gantt widget.
        
        :return     <QTreeWidget>
        """
        return self.uiGanttTREE
    
    def viewWidget( self ):
        """
        Returns the view widget for this gantt widget.
        
        :return     <QGraphicsView>
        """
        return self.uiGanttVIEW
    
    def weekendBrush( self ):
        """
        Returns the weekend brush to be used for coloring in weekends.
        
        :return     <QBrush>
        """
        return self._weekendBrush