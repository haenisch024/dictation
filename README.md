# dictation
Dictate to your computer with simple hotkeys.

## Installation
`pip install dictation`

`dictate`

On the first execution of `dictate` you will be prompted to provide an OpenAI API key. You will need to do this once, unless your API key becomes invalid.

## How To
To begin dictating, press CTRL+SPACE. To stop dictating, release. Your dictation will be cleaned up by GPT and inserted into your clipboard. Hit CTRL+V to paste it where you need it.

## Developer Instructions:

### Making a release:
1. Bump `pyproject.toml` version number.
2. Build the wheel `python -m build`
3. Upload to testpypi with `twine upload --repository testpypi dist/*`
4. Upload to pypi with `twine upload dist/*`