import time
import typer
import pyperclip

import dictation
import dictation.dictation
import dictation.hotkey

app = typer.Typer()

dictation.hotkey.hotkey_start()

@app.command()
def run():
    """Continuously check if Ctrl+Space is pressed or released and record audio accordingly."""
    print("Ready. Press and hold <ctrl>+<space> to dictate. The transcribed dictation will appear in your clipboard when completed.")
    while True:
        # Check hotkey states periodically
        if dictation.hotkey.hotkey_pressed() and not dictation.dictation.is_recording:
            cleaned_text = dictation.dictation.dictate()
            pyperclip.copy(cleaned_text)
            print("Cleaned text copied to clipboard!")

        time.sleep(0.05)  # Small delay to prevent high CPU usage
    
if __name__ == "__main__":
    app()