#!/usr/bin/python

""" Custom backend for managing gantt widget items within the view. """

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

from projexui.qt.QtCore   import QDate,\
                                 QLine,\
                                 QRect,\
                                 Qt
                           
from projexui.qt.QtGui    import QGraphicsScene,\
                                 QLinearGradient,\
                                 QBrush,\
                                 QColor

class XGanttScene(QGraphicsScene):
    def __init__( self, ganttWidget ):
        super(XGanttScene, self).__init__(ganttWidget)
        
        # setup custom properties
        self._ganttWidget       = ganttWidget
        self._hlines            = []
        self._vlines            = []
        self._alternateRects    = []
        self._weekendRects      = []
        self._topLabels         = []
        self._labels            = []
        self._dirty             = True
        
        # create connections
        ganttWidget.dateRangeChanged.connect(self.setDirty)
    
    def dateAt( self, x ):
        """
        Returns the date at the inputed x position.
        
        :return     <QDate>
        """
        gantt       = self.ganttWidget()
        dstart      = gantt.dateStart()
        days        = int(x / float(gantt.cellWidth()))
        
        return dstart.addDays(days)
    
    def dateXPos( self, date ):
        """
        Returns the x-position for the inputed date.
        
        :return     <int>
        """
        gantt    = self.ganttWidget()
        distance = gantt.dateStart().daysTo(date)
        return gantt.cellWidth() * distance
    
    def drawForeground( self, painter, rect ):
        """
        Draws the foreground for this scene.
        
        :param      painter | <QPainter>
                    rect    | <QRect>
        """
        gantt  = self.ganttWidget()
        header = gantt.treeWidget().header()
        width  = self.sceneRect().width()
        height = header.height()
        
        # create the main color
        palette     = gantt.palette()
        color       = palette.color(palette.Button)
        textColor   = palette.color(palette.ButtonText)
        borderColor = color.darker(140)
        text_align  = Qt.AlignBottom | Qt.AlignHCenter
        y           = rect.top()
        
        # create the gradient
        gradient = QLinearGradient()
        gradient.setStart(0, y)
        gradient.setFinalStop(0, y + height)
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, color.darker(120))
        
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, y, width, height)
        
        # add top labels
        for rect, label in self._topLabels:
            rx = rect.x()
            ry = rect.y() + y
            rw = rect.width()
            rh = rect.height()
            
            painter.setPen(borderColor)
            painter.drawRect(rx, ry, rw, rh)
            
            painter.setPen(textColor)
            painter.drawText(rx, ry, rw, rh - 2, text_align, label)
        
        # add bottom labels
        for rect, label in self._labels:
            rx = rect.x()
            ry = rect.y() + y
            rw = rect.width()
            rh = rect.height()
            
            painter.setPen(borderColor)
            painter.drawRect(rx, ry, rw, rh)
            
            painter.setPen(textColor)
            painter.drawText(rx, ry, rw, rh - 2, text_align, label)
    
    def drawBackground( self, painter, rect ):
        """
        Draws the background for this scene.
        
        :param      painter | <QPainter>
                    rect    | <QRect>
        """
        if ( self._dirty ):
            self.rebuild()
        
        # draw the alternating rects
        gantt   = self.ganttWidget()
        
        # draw the alternating rects
        painter.setPen(Qt.NoPen)
        painter.setBrush(gantt.alternateBrush())
        for rect in self._alternateRects:
            painter.drawRect(rect)
        
        # draw the weekends
        painter.setBrush(gantt.weekendBrush())
        for rect in self._weekendRects:
            painter.drawRect(rect)
        
        # draw the default background
        painter.setPen(gantt.gridPen())
        painter.drawLines(self._hlines + self._vlines)
    
    def ganttWidget( self ):
        """
        Returns the gantt view that this scene is linked to.
        
        :return     <XGanttWidget>
        """
        return self._ganttWidget
    
    def isDirty( self ):
        """
        Returns if this gantt widget requires a redraw.
        
        :return     <bool>
        """
        return self._dirty
    
    def rebuild( self ):
        """
        Rebuilds the scene based on the current settings.
        
        :param      start | <QDate>
                    end   | <QDate>
        """
        gantt           = self.ganttWidget()
        start           = gantt.dateStart()
        end             = gantt.dateEnd()
        cell_width      = gantt.cellWidth()
        cell_height     = gantt.cellHeight()
        rect            = self.sceneRect()
        view            = gantt.viewWidget()
        height          = rect.height()
        header          = gantt.treeWidget().header()
        header_height   = header.height()
        
        if ( not header.isVisible() ):
            header_height   = 0
        
        self._labels            = []
        self._hlines            = []
        self._vlines            = []
        self._weekendRects      = []
        self._alternateRects    = []
        self._topLabels         = []
        
        # generate formatting info
        top_format      = 'MMM'
        label_format    = 'd'
        increment       = 1     # days
        
        # generate vertical lines
        x           = 0
        i           = 0
        half        = header_height / 2.0
        curr        = start
        top_label   = start.toString(top_format)
        top_rect    = QRect(0, 0, 0, half)
        alt_rect    = None
        
        while ( curr < end ):
            # update the month rect
            new_top_label = curr.toString(top_format)
            if ( new_top_label != top_label ):
                top_rect.setRight(x)
                self._topLabels.append((top_rect, top_label))
                top_rect  = QRect(x, 0, 0, half)
                top_label = new_top_label
                
                if ( alt_rect is not None ):
                    alt_rect.setRight(x)
                    self._alternateRects.append(alt_rect)
                    alt_rect = None
                else:
                    alt_rect = QRect(x, 0, 0, height)
            
            # create the line
            self._hlines.append(QLine(x, 0, x, height))
            
            # create the header label/rect
            label = str(curr.toString(label_format))
            rect  = QRect(x, half, cell_width, half)
            self._labels.append((rect, label))
            
            # store weekend rectangles
            if ( curr.dayOfWeek() in (6, 7) ):
                rect = QRect(x, 0, cell_width, height)
                self._weekendRects.append(rect)
            
            # increment the dates
            curr = curr.addDays(increment)
            x += cell_width
            i += 1
        
        # update the month rect
        top_rect.setRight(x)
        top_label = end.toString(top_format)
        self._topLabels.append((top_rect, top_label))
        
        if ( alt_rect is not None ):
            alt_rect.setRight(x)
            self._alternateRects.append(alt_rect)
        
        # resize the width to match the last date range
        new_width = x
        self.setSceneRect(0, 0, new_width, height)
        
        # generate horizontal lines
        y       = 0
        h       = height
        width   = new_width
        
        while ( y < h ):
            self._vlines.append(QLine(0, y, width, y))
            y += cell_height
        
        # clear the dirty flag
        self._dirty = False
    
    def setDayWidth( self, width ):
        """
        Sets the day width that will be used for drawing this gantt widget.
        
        :param      width | <int>
        """
        self._dayWidth = width
        
        start   = self.ganttWidget().dateStart()
        end     = self.ganttWidget().dateEnd()
        
        self._dirty = True
    
    def setDirty( self, state = True ):
        """
        Sets the dirty state for this scene.  When the scene is dirty, it will
        be rebuilt on the next draw.
        
        :param      state | <bool>
        """
        self._dirty = state
    
    def setSceneRect( self, *args ):
        """
        Overloads the set rect method to signal that the scene needs to be 
        rebuilt.
        
        :param      args | <arg variant>
        """
        super(XGanttScene, self).setSceneRect(*args)
        
        self._dirty = True