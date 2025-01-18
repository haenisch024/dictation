import keyboard
import time
import typer
import pyperclip

import dictation
import dictation.dictation

app = typer.Typer()

@app.command()
def run():
    """Continuously check if Ctrl+Space is pressed or released and record audio accordingly."""
    while True:
        # Check hotkey states periodically
        if dictation.dictation.hotkey_pressed() and not dictation.dictation.is_recording:
            cleaned_text = dictation.dictation.dictate()
            pyperclip.copy(cleaned_text)
            print("Cleaned text copied to clipboard!")

        time.sleep(0.05)  # Small delay to prevent high CPU usage
    
if __name__ == "__main__":
    app()