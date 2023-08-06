#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
This module contains the symbol matcher mode
"""
from pyqode.core.mode import Mode
from pyqode.core.decoration import TextDecoration
from pyqode.qt import QtGui, QtCore


class SymbolMatcherMode(Mode):
    """
    Do symbols matches highlighting (parenthesis, braces, ...).

    .. note:: This mode requires the document to be filled with :class:`pyqode.core.TextBlockUserData`,
              i.e. a :class:`pyqode.core.SyntaxHighlighter` must be installed on
              the editor instance.
    """
    IDENTIFIER = "symbolMatcherMode"
    DESCRIPTION = "Highlight matching symbols (paren, braces, brackets,...)"

    def __init__(self):
        Mode.__init__(self)
        self.__decorations = []

    def _onInstall(self, editor):
        Mode._onInstall(self, editor)
        self.editor.style.addProperty("matchedBraceBackground",
                                      QtGui.QColor("#B4EEB4"))
        self.editor.style.addProperty("matchedBraceForeground",
                                      QtGui.QColor("#FF0000"))

    def _onStateChanged(self, state):
        if state:
            self.editor.cursorPositionChanged.connect(self.doSymbolsMatching)
        else:
            self.editor.cursorPositionChanged.disconnect(self.doSymbolsMatching)

    def matchParentheses(self, parentheses, cursorPosition):
        for i, info in enumerate(parentheses):
            cursorPos = (self.editor.textCursor().position() -
                         self.editor.textCursor().block().position())
            if info.character == "(" and info.position == cursorPos:
                self.createParenthesisSelection(
                    cursorPosition + info.position,
                    self.matchLeftParenthesis(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == ")" and info.position == cursorPos - 1:
                self.createParenthesisSelection(
                    cursorPosition + info.position,
                    self.matchRightParenthesis(
                        self.editor.textCursor().block(), i - 1, 0))

    def matchLeftParenthesis(self, currentBlock, i, cpt):
        try:
            data = currentBlock.userData()
            parentheses = data.parentheses
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "(":
                    cpt += 1
                    continue
                if info.character == ")" and cpt == 0:
                    self.createParenthesisSelection(currentBlock.position() +
                                                    info.position)
                    return True
                elif info.character == ")":
                    cpt -= 1
            currentBlock = currentBlock.next()
            if currentBlock.isValid():
                return self.matchLeftParenthesis(currentBlock, 0, cpt)
            return False
        except RuntimeError:  # recursion limit exceeded when working with
                              # big files
            return False

    def matchRightParenthesis(self, currentBlock, i, numRightParentheses):
        try:
            data = currentBlock.userData()
            parentheses = data.parentheses
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == ")":
                    numRightParentheses += 1
                    continue
                if info.character == "(":
                    if numRightParentheses == 0:
                        self.createParenthesisSelection(
                            currentBlock.position() + info.position)
                        return True
                    else:
                        numRightParentheses -= 1
            currentBlock = currentBlock.previous()
            if currentBlock.isValid():
                data = currentBlock.userData()
                parentheses = data.parentheses
                return self.matchRightParenthesis(
                    currentBlock, len(parentheses) - 1, numRightParentheses)
            return False
        except RuntimeError:  # recursion limit exeeded when working in big files
            return False

    def matchSquareBrackets(self, brackets, cursorPosition):
        for i, info in enumerate(brackets):
            cursorPos = (self.editor.textCursor().position() -
                         self.editor.textCursor().block().position())
            if info.character == "[" and info.position == cursorPos:
                self.createParenthesisSelection(
                    cursorPosition + info.position,
                    self.matchLeftBracket(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == "]" and info.position == cursorPos - 1:
                self.createParenthesisSelection(
                    cursorPosition + info.position, self.matchRightBracket(
                        self.editor.textCursor().block(), i - 1, 0))

    def matchLeftBracket(self, currentBlock, i, cpt):
        try:
            data = currentBlock.userData()
            parentheses = data.squareBrackets
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "[":
                    cpt += 1
                    continue
                if info.character == "]" and cpt == 0:
                    self.createParenthesisSelection(
                        currentBlock.position() + info.position)
                    return True
                elif info.character == "]":
                    cpt -= 1
            currentBlock = currentBlock.next()
            if currentBlock.isValid():
                return self.matchLeftBracket(currentBlock, 0, cpt)
            return False
        except RuntimeError:
            return False

    def matchRightBracket(self, currentBlock, i, numRightParentheses):
        try:
            data = currentBlock.userData()
            parentheses = data.squareBrackets
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == "]":
                    numRightParentheses += 1
                    continue
                if info.character == "[":
                    if numRightParentheses == 0:
                        self.createParenthesisSelection(
                            currentBlock.position() + info.position)
                        return True
                    else:
                        numRightParentheses -= 1
            currentBlock = currentBlock.previous()
            if currentBlock.isValid():
                data = currentBlock.userData()
                parentheses = data.squareBrackets
                return self.matchRightBracket(
                    currentBlock, len(parentheses) - 1, numRightParentheses)
            return False
        except RuntimeError:
            return False

    def matchBraces(self, braces, cursorPosition):
        for i, info in enumerate(braces):
            cursorPos = (self.editor.textCursor().position() -
                         self.editor.textCursor().block().position())
            if info.character == "{" and info.position == cursorPos:
                self.createParenthesisSelection(
                    cursorPosition + info.position,
                    self.matchLeftBrace(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == "}" and info.position == cursorPos - 1:
                self.createParenthesisSelection(
                    cursorPosition + info.position, self.matchRightBrace(
                        self.editor.textCursor().block(), i - 1, 0))

    def matchLeftBrace(self, currentBlock, i, cpt):
        try:
            data = currentBlock.userData()
            parentheses = data.braces
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "{":
                    cpt += 1
                    continue
                if info.character == "}" and cpt == 0:
                    self.createParenthesisSelection(
                        currentBlock.position() + info.position)
                    return True
                elif info.character == "}":
                    cpt -= 1
            currentBlock = currentBlock.next()
            if currentBlock.isValid():
                return self.matchLeftBrace(currentBlock, 0, cpt)
            return False
        except RuntimeError:
            return False

    def matchRightBrace(self, currentBlock, i, numRightParentheses):
        try:
            data = currentBlock.userData()
            parentheses = data.braces
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == "}":
                    numRightParentheses += 1
                    continue
                if info.character == "{":
                    if numRightParentheses == 0:
                        self.createParenthesisSelection(
                            currentBlock.position() + info.position)
                        return True
                    else:
                        numRightParentheses -= 1
            currentBlock = currentBlock.previous()
            if currentBlock.isValid():
                data = currentBlock.userData()
                parentheses = data.braces
                return self.matchRightBrace(
                    currentBlock, len(parentheses) - 1, numRightParentheses)
            return False
        except RuntimeError:
            return False

    def doSymbolsMatching(self):
        for d in self.__decorations:
            self.editor.removeDecoration(d)
        self.__decorations[:] = []
        data = self.editor.textCursor().block().userData()
        if data:
            pos = self.editor.textCursor().block().position()
            self.matchParentheses(data.parentheses, pos)
            self.matchSquareBrackets(data.squareBrackets, pos)
            self.matchBraces(data.braces, pos)

    def createParenthesisSelection(self, pos, match=True):
        cursor = self.editor.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(cursor.NextCharacter, cursor.KeepAnchor)
        d = TextDecoration(cursor, draw_order=10)
        if match:
            # d.setForeground(QtGui.QBrush(QtGui.QColor("#FF8647")))
            f = self.editor.style.value("matchedBraceForeground")
            if f:
                d.setForeground(f)
            b = self.editor.style.value("matchedBraceBackground")
            if b:
                d.setBackground(b)
        else:
            d.setForeground(QtCore.Qt.red)
        self.__decorations.append(d)
        self.editor.addDecoration(d)
