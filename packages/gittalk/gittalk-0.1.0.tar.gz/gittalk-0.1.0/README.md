gittalk
=======

Imagine you are working on a hack, and you just pushed some code. 
Instead of yelling to your teammates and letting them aware of the 
changes, wouldn't it be cool to have the computer say it out loud 
for you?   

## Installation

`pip install gittalk`     

`python setup.py install` should also be just fine, in case you don't 
have Pip installed.

## Dependencies

* `pyttsx`: https://pypi.python.org/pypi/pyttsx

The file `requirements.txt` contains all other dependencies I've used 
while working on `gittalk`, though most of them are not needed in 
running this program.

Pyttsx will also install its own dependencies.

## Doesn't work?

Most likely, the installation for pyttsx failed. Check out 
https://github.com/parente/pyttsx and see if any previously raised 
issues there are helpful. Unfortunately, I've only tested this on 
Ubuntu 12.10 32-bit, so it might not work as expected on Windows/OSX...   

## Features and Usage

* Make a git commit as usual. Then type `gittalk` on the terminal. The 
last commit message should be said out loud. :D

* ... More to come! (see `say_last_push` in `gittalk/core.py` for example)

## Notes
This is still pretty basic, and is mostly my attempt at playing with 
different TTS (text-to-speech) packages in Python, as well as learning 
how to structure a proper Python package and share it via Pip.  

That said, I do plan to extend it further and make this even more fun 
and useful. Please send me a pull request if you would like to 
contribute. Suggestions/criticism/advice are all welcome!
