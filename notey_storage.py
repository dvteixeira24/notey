import datetime
import pickle


class Note(object):
    def __init__(self, text="No text entered.", deadline=None, completed=False):
        if deadline is not None:
            self.deadline = deadline
        self.text = text
        self.completed = completed
        self.creation_date = datetime.datetime.now()

    def __repr__(self):
        s = ''
        if hasattr(self, 'deadline'):
            s = ' ' + self.deadline.strftime('%d-%m-%Y %H:%M')
        if self.completed:
            s = s + "(Completed)"

        return self.creation_date.strftime('%d-%m-%Y %H:%M') + ' ' + self.text + s 


def notesFromFile():
    with open('notes.pickle', 'rb') as f:
        notes = pickle.load(f)
        return notes


# Accepts
def notesToFile(notes):
    with open('notes.pickle', 'wb') as f:
        pickle.dump(notes, f)

def test_f():
    print("Running note pickling test.")

    test_notes = [Note("A cool new note!"),
                  Note("Another great note."),
                  Note("This one has a deadline.", datetime.datetime.strptime('2022-07-20 18:02:24.000000',
                                                                                   '%Y-%m-%d %H:%M:%S.%f')),
                  Note("Another slick note."),
                  Note("Check this note out!"),
                  Note("Here's a note with a lot of text. Adding a lot of text to your note will cause it to wrap. This means note text can go over multiple lines in your notes view."),
                  Note("Another with a deadline.", datetime.datetime.strptime('2023-09-21 12:21:14.000000',
                                                                                   '%Y-%m-%d %H:%M:%S.%f'))]

    i = len(test_notes)
    for note in test_notes:
        note.creation_date = note.creation_date - datetime.timedelta(seconds=100000*i)
        i = i-1
        print(note)

    notesToFile(test_notes)
    print("Wrote notes to file.")
    read_notes = notesFromFile()
    print("Got these notes from file:")
    for note in read_notes:
        print(note)
