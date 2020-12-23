# Openbox Pipemenu written in Python3 
openbox pipemenu for applications menu written in ```Python3```

Obamenu is pipemenu for openbox windows manager. There are some forks for obamenu here and there but none of them worked for me with python3.
Python2 will no longer have support after 2020, it has to be replaced with Python3. So I have decided to maintain my own version.
Script generally will read *.desktop* files from */usr/share/applications* and flatpak desktop files.

## Revisions and Additions
This version has a lot of updates, revisions and additions. A short list for them is;
- It is written to work with latest Python version. (Py3.9.1 when this is coded)
- Menu items are now alphabetically ordered (one of most important features)
- Algorithm will try to find all possible icons searching icon theme directories recursively
- Desktop items will not be added to Menu if "Exec" command couldn't be found on system
- Some applications can have duplicate icons in theme folders, best option shall be selected
- Automatic and direct theme selection option added
- Flatpak applications support added

## Installation
1. Download the file *obamenu.py*, and unpack it somewhere. 
2. Make sure it is executable, either by right click-properties or typing ```chmod 754 obamenu.py``` in your terminal.
3. Don't forget to edit terminal string in *obamenu.py*, write here your terminal of choice. 
4. Edit your menu.xml file (normally found in *./config/openbox/*) or use obmenu, obmenu-qt, kickshaw, etc.  Path to *menu.xml* would differ according to your openbox setup.
5. Insert the following lines in your menu.xml. Path to *obamenu.py* would differ according to where you have unpacked it. It is usually your openbox config directory.
```
<menu execute="~/.path/to/obamenu.py" id="My Menu" label="Applications" />
```
6. Reconfigure openbox either by logout or typing ```openbox --reconfigure"``` in your terminal
7. You should now see your applications under the Applications menu.

## Notes
Although I have wrote most of new codes myself there are some copy+paste too.
There are some codes from other forks of obamenu which I had forgot where I gathered.
All codes I had found was for Python2 actually, I may have revised them a bit or used them directly.
Please don't get mad if I didn't mentioned about your name.

Regards

### Original version
Original obamenu (v1.1.7) can be found here :http://rmoe.anukis.de/obamenu.html
