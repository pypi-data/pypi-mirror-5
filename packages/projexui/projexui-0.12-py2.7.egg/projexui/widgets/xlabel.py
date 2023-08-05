""" Defines some additional features for a basic QLabel """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software, LLC'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software, LLC'
__email__           = 'team@projexsoftware.com'

from projexui.qt import Signal, Slot, Property
from projexui.qt.QtCore import Qt
from projexui.qt.QtGui import QLabel,\
                              QLineEdit

class XLabel(QLabel):
    editingFinished = Signal()
    
    def __init__( self, parent = None ):
        super(XLabel, self).__init__(parent)
        
        self._editable  = False
        self._lineEdit  = None
    
    @Slot()
    def acceptEdit( self ):
        """
        Accepts the current edit for this label.
        """
        if ( not self._lineEdit ):
            return
        
        self.setText(self._lineEdit.text())
        self._lineEdit.hide()
        
        if ( not self.signalsBlocked() ):
            self.editingFinished.emit()
    
    def beginEdit( self ):
        """
        Begins editing for the label.
        """
        if ( not self._lineEdit ):
            return
        
        self._lineEdit.setText(self.text())
        self._lineEdit.show()
        self._lineEdit.selectAll()
        self._lineEdit.setFocus()
    
    def eventFilter( self, object, event ):
        """
        Filters the event for the inputed object looking for escape keys.
        
        :param      object | <QObject>
                    event  | <QEvent>
        
        :return     <bool>
        """
        if ( event.type() == event.KeyPress ):
            if ( event.key() == Qt.Key_Escape ):
                self.rejectEdit()
                return True
            
            elif ( event.key() in (Qt.Key_Return, Qt.Key_Enter) ):
                self.acceptEdit()
                return True
        
        elif ( event.type() == event.FocusOut ):
            self.acceptEdit()
        
        return False
    
    def isEditable( self ):
        """
        Returns if this label is editable or not.
        
        :return     <bool>
        """
        return self._editable
    
    def lineEdit( self ):
        """
        Returns the line edit instance linked with this label.  This will be
        null if the label is not editable.
        
        :return     <QLineEdit>
        """
        return self._lineEdit
    
    def mouseDoubleClickEvent( self, event ):
        """
        Prompts the editing process if the label is editable.
        
        :param      event | <QMouseDoubleClickEvent>
        """
        if ( self.isEditable() ):
            self.beginEdit()
        
        super(XLabel, self).mouseDoubleClickEvent(event)
    
    def rejectEdit( self ):
        """
        Cancels the edit for this label.
        """
        if ( self._lineEdit ):
            self._lineEdit.hide()
    
    def resizeEvent( self, event ):
        """
        Resize the label and the line edit for this label.
        
        :param      event | <QResizeEvent>
        """
        super(XLabel, self).resizeEvent(event)
        
        if ( self._lineEdit ):
            self._lineEdit.resize(self.size())
    
    def setEditable( self, state ):
        """
        Sets whether or not this label should be editable or not.
        
        :param      state | <bool>
        """
        self._editable = state
        
        if ( state and not self._lineEdit ):
            self.setLineEdit(QLineEdit(self))
        
        elif ( not state and self._lineEdit ):
            self._lineEdit.close()
            self._lineEdit.setParent(None)
            self._lineEdit.deleteLater()
            self._lineEdit = None
    
    def setLineEdit( self, lineEdit ):
        """
        Sets the line edit instance for this label.
        
        :param      lineEdit | <QLineEdit>
        """
        self._lineEdit = lineEdit
        if ( lineEdit ):
            lineEdit.setFont(self.font())
            lineEdit.installEventFilter(self)
            lineEdit.resize(self.size())
            lineEdit.hide()
    
    x_editable = Property(bool, isEditable, setEditable)

__designer_plugins__ = [XLabel]