# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import datetime

from PySide2.QtCore import Qt, QEvent, QObject, QDateTime, QDir
from PySide2.QtGui import QPainter, QIcon

import notey_storage
from PySide2.QtWidgets import QApplication, QMainWindow, QStyledItemDelegate, QLayout, QGridLayout, QWidget, QLabel,QListWidgetItem
from PySide2.QtUiTools import QUiLoader


class NoteWidgetCustom(QWidget):  # Modified QWidget class.
    def __init__(self, parent, note=None):
        super(NoteWidgetCustom, self).__init__(parent)
        with open("qss/note.qsst", "r") as f:
            _style = f.read()
            self.setStyleSheet(_style)

        QGridLayout(self)
        loader = QUiLoader()
        self.ui = loader.load("note.ui")
        self.layout().addWidget(self.ui)
        self.layout().setMargin(0)
        self.ui.date.setText(note.creation_date.strftime("%d/%m/%Y %H:%M"))
        if hasattr(note, "deadline"):
            self.ui.deadline.setText(note.deadline.strftime("%d/%m/%Y %H:%M"))
            self.ui.deadline.setStyleSheet("QLabel { color: #1B3D7D; }")
        else:
            self.ui.deadline.setText("")
        self.ui.markcompleted.setIcon(QIcon('images/checkbox_unchecked.png'))
        if note.completed == True:
            self.ui.markcompleted.setIcon(QIcon('images/checkbox_checked.png'))
            self.ui.deadline.setText("Completed")
            self.ui.deadline.setStyleSheet("QLabel { color: #23C02E; }")
        self.ui.content.setText(note.text)
        self.main_window = self.parent()

        # Connect note widget option buttons
        self.ui.markcompleted.clicked.connect(self.toggleCompleted)
        self.ui.deletenote.clicked.connect(self.delete)
        self.ui.editnote.clicked.connect(self.edit)
       
        self.note = note
        

    def enterEvent(self, event):
        self.ui.note_stacked_widget.setCurrentIndex(1)

    def leaveEvent(self, event):
        self.ui.note_stacked_widget.setCurrentIndex(0)

    def toggleCompleted(self):
        if hasattr(self.note, "deadline"):
            self.ui.deadline.setStyleSheet("QLabel { color: #1B3D7D; }")
            self.ui.deadline.setText(self.note.deadline.strftime("%d/%m/%Y %H:%M"))
        else:
            self.ui.deadline.setText("")
        if not self.note.completed:
            self.ui.deadline.setText("Completed")
            self.ui.deadline.setStyleSheet("QLabel { color: #23C02E; }")
            self.ui.markcompleted.setIcon(QIcon('images/checkbox_checked.png'))
        else:
            self.ui.markcompleted.setIcon(QIcon('images/checkbox_unchecked.png'))
        self.main_window.markCompleted(self.note)

    def delete(self):
        self.main_window.deleteNote(self.note)

    def edit(self):
        editor = NoteEditor(self.main_window, self.note)

class NoteEditor(QObject):
    def __init__(self, main_window, note):
        super(NoteEditor, self).__init__()
        self.main_window = main_window
        self.old_note = note
        self.new_note = notey_storage.Note()
        self.new_note.creation_date = note.creation_date
        self.ui = QUiLoader().load("edit.ui")
        with open("qss/window.qsst", "r") as f:
            _style = f.read()
            self.ui.setStyleSheet(_style)
        self.ui.textEdit.setText(note.text)
        self.ui.dateTimeEdit.hide()
        if hasattr(note, "deadline"):
            self.ui.checkBox.setChecked(True)
            self.ui.dateTimeEdit.setDateTime(QDateTime.fromString(note.deadline.strftime("%d/%m/%Y %H:%M"), "d/M/yyyy hh:mm"))
            self.ui.dateTimeEdit.show()

        self.ui.accepted.connect(self.saveNote)
        self.ui.checkBox.stateChanged.connect(self.toggleDeadlineEdit)
        self.ui.exec()

    def saveNote(self):
        if self.ui.checkBox.isChecked():
            setattr(self.new_note, 'deadline', self.ui.dateTimeEdit.dateTime().toPython())
        self.new_note.text = self.ui.textEdit.toPlainText()
        self.main_window.editNote(self.old_note, self.new_note)

    def toggleDeadlineEdit(self, state):
        if state == 2:
            self.ui.dateTimeEdit.show()
        else:
            self.ui.dateTimeEdit.hide()


    
class MainWindow(QMainWindow):
    def __init__(self, notes):
        super(MainWindow, self).__init__()
        self.setWindowTitle("notey")
        self.setWindowIcon(QIcon('icon.png'))
        with open("qss/window.qsst", "r") as f:
            _style = f.read()
            self.setStyleSheet(_style)
        loader = QUiLoader(self)
        self.ui = loader.load("form.ui")
        self.ui.nav_bar_buttongroup.buttonToggled.connect(self.navigation_event)
        self.setCentralWidget(self.ui)
        self.notes = notes
        self.reloadNotes()
        self.ui.new_note_datetime_edit.hide()
        self.ui.save.clicked.connect(self.addNoteFromForm)
        self.ui.checkBox.stateChanged.connect(self.toggleDeadlineEdit)
        self.ui.new_note_datetime_edit.setDateTime(QDateTime.fromString(datetime.datetime.now().strftime("%d/%m/%Y"), "d/M/yyyy"))

    def toggleDeadlineEdit(self, state):
        if state == 2:
            self.ui.new_note_datetime_edit.show()
        else:
            self.ui.new_note_datetime_edit.hide()

    def reloadNotes(self):
        self.notes = notey_storage.notesFromFile()
        self.note_widgets = []
        self.note_items = []
        self.ui.notes_listview.clear()
        for note in reversed(self.notes):
            self.load_note(note)

    def load_note(self, note):
        self.note_widgets.append(NoteWidgetCustom(self, note))
        self.note_items.append(QListWidgetItem(self.ui.notes_listview))
        self.note_items[-1].setSizeHint(self.note_widgets[-1].sizeHint())
        self.note_widgets[-1].setObjectName(note.creation_date.strftime("%d:%m:%Y %H:%M:%S %f"))
        self.ui.notes_listview.insertItem(0, self.note_items[-1])
        self.ui.notes_listview.setItemWidget(self.note_items[-1], self.note_widgets[-1])
    
    def navigation_event(self, button):
        if button.isChecked():
            getattr(self, "%s_activate" % button.objectName())()

    def notes_btn_activate(self):
        self.ui.stacked_widget.setCurrentIndex(0)
        self.ui.title_label.setText("notey")

    def new_btn_activate(self):
        self.ui.stacked_widget.setCurrentIndex(1)
        self.ui.title_label.setText("new note")

    def getSelfNote(self, note):
        return next((n for n in self.notes if n.creation_date == note.creation_date), None)

    def markCompleted(self, note):
        self.getSelfNote(note).completed = not self.getSelfNote(note).completed
        notey_storage.notesToFile(self.notes)

    def deleteNote(self, note):
        self.notes.remove(note)
        notey_storage.notesToFile(self.notes)
        self.reloadNotes()

    def editNote(self, old_note, new_note):
        self.getSelfNote(old_note).text = new_note.text
        if hasattr(new_note, "deadline"):
            self.getSelfNote(old_note).deadline = new_note.deadline
        else:
            if hasattr(old_note, "deadline"):
                del(self.getSelfNote(old_note).deadline)
        notey_storage.notesToFile(self.notes)
        self.reloadNotes()
    
    def addNote(self, note):
        self.notes.append(note)
        notey_storage.notesToFile(self.notes)
        self.reloadNotes()
        self.ui.text_edit.setText("Write your note here.")

    def addNoteFromForm(self):
        note_to_add = notey_storage.Note(self.ui.text_edit.toPlainText())
        if self.ui.checkBox.isChecked():
            note_to_add.deadline = self.ui.new_note_datetime_edit.dateTime().toPython()
        self.addNote(note_to_add)
        self.ui.notes_btn.click()
      


if __name__ == "__main__":
    app = QApplication()
    root = os.path.dirname(os.path.abspath(__file__))   
    QDir.addSearchPath('svg', os.path.join(root, 'images'))
    QDir.addSearchPath('images', os.path.join(root, 'images'))
    notes = notey_storage.notesFromFile()
    widget = MainWindow(notes)
    widget.show()
    sys.exit(app.exec_())

