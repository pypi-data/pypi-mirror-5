""" [desc] """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

from projexui.qt import Signal
from projexui.qt.QtCore import Qt
from projexui.qt.QtGui import QWidget
from projexui.widgets.xlineedit import XLineEdit

from orb import Query, QueryCompound

import projexui

class XOrbQueryEntryWidget(QWidget):
    """ """
    def __init__( self, parent, tableType ):
        super(XOrbQueryEntryWidget, self).__init__( parent )
        
        # load the user interface
        projexui.loadUi(__file__, self)
        
        # define custom properties
        self._queryWidget       = parent.queryWidget()
        self._containerWidget   = parent
        self._tableType         = tableType
        self._query             = None
        self._first             = False
        self._last              = False
        
        # create connections
        self.uiAddBTN.clicked.connect(self.addEntry)
        self.uiRemoveBTN.clicked.connect(self.removeEntry)
        self.uiMoveUpBTN.clicked.connect(self.moveUp)
        self.uiMoveDownBTN.clicked.connect(self.moveDown)
        self.uiEnterBTN.clicked.connect(self.enterCompound)
        self.uiColumnDDL.currentIndexChanged.connect(self.assignPlugin)
        self.uiOperatorDDL.currentIndexChanged.connect(self.assignEditor)
        self.uiJoinDDL.currentIndexChanged.connect(self.updateJoin)
        
        # set default properties
        col_names = tableType.schema().columnNames()
        col_names = filter(lambda x: not x.startswith('_'), col_names)
        self.uiColumnDDL.addItems(sorted(col_names))
    
    def addEntry(self):
        self._containerWidget.addEntry(entry=self)
    
    def assignPlugin(self):
        """
        Assigns an editor based on the current column for this schema.
        """
        self.uiOperatorDDL.blockSignals(True)
        self.uiOperatorDDL.clear()
        
        plugin = self.currentPlugin()
        if plugin:
            self.uiOperatorDDL.addItems(plugin.operators())
        
        self.uiOperatorDDL.blockSignals(False)
        self.assignEditor()
    
    def assignEditor(self):
        """
        Assigns the editor for this entry based on the plugin.
        """
        plugin = self.currentPlugin()
        column = self.currentColumn()
        value = self.currentValue()
        
        if not plugin:
            self.setEditor(None)
            return
        
        self.setUpdatesEnabled(False)
        self.blockSignals(True)
        op = self.uiOperatorDDL.currentText()
        self.setEditor(plugin.createEditor(self, column, op, value))
        self.setUpdatesEnabled(True)
        self.blockSignals(False)
    
    def currentColumn(self):
        table = self.tableType()
        if not table:
            return None
        
        col_name = self.uiColumnDDL.currentText()
        schema   = self.tableType().schema()
        column   = table.schema().column(str(col_name))
        
        return column
    
    def currentPlugin(self):
        column = self.currentColumn()
        if not column:
            return None
        
        return self.pluginFactory().plugin(column)
    
    def currentValue(self):
        plugin = self.currentPlugin()
        value = None
        if plugin:
            value = plugin.editorValue(self.editor())
        
        if value is None and self._query is not None:
            q_value = self._query.value()
            if q_value != Query.UNDEFINED:
                value = q_value
        
        return value
    
    def editor(self):
        """
        Returns the editor instance for this widget.
        
        :return     <QWidget> || None
        """
        return self.uiEditorAREA.widget()
    
    def enterCompound(self):
        self._containerWidget.enterCompound(self, self.query())
    
    def isChecked(self):
        """
        Returns whether or not this widget is checked.
        
        :return     <bool>
        """
        return self.uiSelectCHK.isChecked()
    
    def moveDown(self):
        self._containerWidget.moveDown(self)
    
    def moveUp(self):
        self._containerWidget.moveUp(self)
    
    def query(self):
        """
        Returns the query instance for this widget.
        
        :return     <orb.Query> || <orb.QueryCompound>
        """
        queryWidget = self.queryWidget()
        
        # check to see if there is an active container for this widget
        container = queryWidget.containerFor(self)
        if container:
            return container.query()
        
        elif QueryCompound.typecheck(self._query):
            return self._query
        
        # generate a new query from the editor
        column = str(self.uiColumnDDL.currentText())
        plugin = self.currentPlugin()
        editor = self.editor()
        op     = self.uiOperatorDDL.currentText()
        
        if column and plugin:
            query = Query(column)
            plugin.setupQuery(query, op, editor)
            return query
        else:
            return Query()
    
    def joiner(self):
        """
        Returns the joiner operator type for this entry widget.
        
        :return     <QueryCompound.Op>
        """
        if self.uiJoinDDL.currentIndex():
            return QueryCompound.Op.Or
        return QueryCompound.Op.And
    
    def queryWidget(self):
        return self._queryWidget
    
    def pluginFactory(self):
        return self._queryWidget.pluginFactory()
    
    def refreshButtons(self):
        last = self._last
        first = self._first
        
        self.uiJoinDDL.setVisible(not last)
        self.uiJoinDDL.setEnabled(first)
        self.uiMoveUpBTN.setEnabled(not first)
        self.uiMoveDownBTN.setEnabled(not last)
        self.uiEnterBTN.setEnabled(QueryCompound.typecheck(self._query))
    
    def removeEntry(self):
        self._containerWidget.removeEntry(self)
    
    def setChecked(self, state):
        self.uiSelectCHK.setChecked(False)
    
    def setEditor(self, editor):
        """
        Sets the editor widget for this entry system.
        
        :param      editor | <QWidget> || None
        """
        widget = self.uiEditorAREA.takeWidget()
        if widget:
            widget.close()
            widget.deleteLater()
        
        if editor:
            editor.setMinimumHeight(28)
            self.uiEditorAREA.setWidget(editor)
    
    def setQuery(self, query):
        """
        Sets the query instance for this widget to the inputed query.
        
        :param      query | <orb.Query> || <orb.QueryCompound>
        """
        self._query = query
        
        if QueryCompound.typecheck(query):
            self.uiColumnDDL.hide()
            self.uiOperatorDDL.hide()
            
            # setup the compound editor
            editor = XLineEdit(self)
            editor.setReadOnly(True)
            editor.setText(query.name())
            editor.setHint('compound')
            
            self.setEditor(editor)
        
        else:
            self.uiColumnDDL.show()
            self.uiOperatorDDL.show()
            
            text = query.columnName()
            index = self.uiColumnDDL.findText(text)
            self.uiColumnDDL.setCurrentIndex(index)
            if index == -1:
                self.uiColumnDDL.lineEdit().setText(text)
            
            self.uiOperatorDDL.blockSignals(True)
            plug = self.currentPlugin()
            if plug:
                op = plug.operator(query.operatorType(), query.value())
                
                index = self.uiOperatorDDL.findText(op)
                if index != -1:
                    self.uiOperatorDDL.setCurrentIndex(index)
            
            self.uiOperatorDDL.blockSignals(False)
            
            self.assignEditor()
        
        self.refreshButtons()
    
    def setFirst(self, first):
        self._first = first
        self.refreshButtons()
    
    def setLast(self, last):
        self._last = last
        self.refreshButtons()
        
    def setJoiner(self, joiner):
        """
        Sets the join operator type for this entry widget to the given value.
        
        :param      joiner | <QueryCompound.Op>
        """
        if joiner == QueryCompound.Op.And:
            self.uiJoinDDL.setCurrentIndex(0)
        else:
            self.uiJoinDDL.setCurrentIndex(1)
    
    def updateJoin(self):
        text = self.uiJoinDDL.currentText()
        if text == 'and':
            joiner = QueryCompound.Op.And
        else:
            joiner = QueryCompound.Op.Or
        
        self._containerWidget.setCurrentJoiner(joiner)
    
    def tableType(self):
        return self._tableType