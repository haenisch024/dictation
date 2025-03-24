import typer
from dictation_pkg.dictation import dictate

app = typer.Typer()

@app.command()
def run():
    """Continuously check if Ctrl+Space is pressed or released and record audio accordingly."""      
    agenda = input('Is there an agenda for this meeting? Enter "The Agenda" or enter "n" for No Agenda and press Enter: ')
    if agenda.lower() != "n":
        print("Agenda set to:", agenda)
    print("Ready. Press <ctrl>+<space> to start dictate, press <ctrl>+<space> again to stop dictate. The transcribed dictation will appear in your clipboard when completed.")
    dictate()
    
if __name__ == "__main__":
    app()