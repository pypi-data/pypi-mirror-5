""" Defines a search edit for the line edit. """

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

from projexui import resources
from projexui.widgets.xlineedit import XLineEdit
from projexui.qt.QtGui import QToolButton, QIcon


class XSearchEdit(XLineEdit):
    def __init__(self, parent=None):
        super(XSearchEdit, self).__init__(parent)
        
        # setup custom properties
        self._cancelButton = QToolButton(self)
        self._cancelButton.setIcon(QIcon(resources.find('img/remove_dark.png')))
        self._cancelButton.setAutoRaise(True)
        self._cancelButton.setToolTip('Clear Search Text')
        self._cancelButton.hide()
        self.addButton(self._cancelButton)
        
        # setup default properties
        self.setHint('enter search')
        self.setIcon(QIcon(resources.find('img/search.png')))
        self.setCornerRadius(8)
        self.adjustStyleSheet()
        self.adjustTextMargins()
        
        # create connections
        self._cancelButton.clicked.connect(self.clear)
        self.textChanged.connect(self.toggleCancelButton)
    
    def clear(self):
        """
        Clears the search text for this instance.
        """
        super(XLineEdit, self).clear()
        
        self.textEntered.emit('')
    
    def toggleCancelButton(self):
        """
        Toggles the visibility for the cancel button based on the current
        text.
        """
        self._cancelButton.setVisible(self.text() != '')

__designer_plugins__ = [XSearchEdit]