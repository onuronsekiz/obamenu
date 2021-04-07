#!/usr/bin/env python3
#
# Version 3.0.0
# Revised: onuronsekiz (overlord)
# Original Author: rmoe (v1.1.7)
#
# / revisions and additions:
#
# - recoded for python 3.9+
# - menu sort for both categories and programs
# - finding all possible icons by searching deeply in themes
# - icon search algorithm for faster approach 
# - desktop item ignored if Exec command not found in system
# - automatic and direct theme selection if possible
# - flatpak applications support
# - duplicate icon handling
#
# ----- config ---

import subprocess, glob, os

userhome = os.path.expanduser('~')
applications_dirs = ("/usr/share/applications", userhome + "/.local/share/applications","/var/lib/flatpak/exports/share/applications")
image_dir_base = ("/usr/share", "/var/lib/flatpak/exports/share") # without "pixmaps" -/usr/local/share in FreeBSD, /usr/share on linux
try: #automatic theme selection
	with open(userhome + "/.gtkrc-2.0", 'r') as readobj:
		for line in readobj:
				if "gtk-icon-theme-name" in line:
					selected_theme=line.split("\"")[1] 
except IOError:
	selected_theme = "Adwaita" #fallback theme

#selected_theme = "gnome" # direct theme selection, don't make it hicolor.   ***** SOME DISTRIBUTIONS REQUIRES THIS OPTION UNCOMMENTED.
application_groups = ("AudioVideo", "Development", "Editors",  "Engineering", "Games", "Graphics", "Internet",  "Multimedia", "Office",  "Other",  "Settings", "System",  "Utilities") # enter here new category as you wish, it will be sorted 
group_aliases = {"Audio":"Multimedia","Video":"Multimedia","AudioVideo":"Multimedia","Network":"Internet","Game":"Games", "Utility":"Utilities", "Development":"Editors","GTK":"",  "GNOME":""}
ignoreList = ("gtk3-icon-browser","evince-previewer", "Ted",  "wingide3.2", "python3.4", "feh","xfce4-power-manager-settings", "picom","compton","yad-icon-browser" )
prefixes = ("legacy","categories","apps","devices","mimetypes","places","preferences","actions", "status","emblems") #added for prefered icon dirs and sizes. could be gathered automatically but wouldn't be sorted like this
iconSizes = ("48","32","24","16","48x48","40x40","36x36","32x32","24x24","64x64","72x72","96x96","16x16","128x128","256x256","scalable","apps","symbolic")
terminal_string = "xterm -e"         # your favourites terminal exec string
simpleOBheader = True  # print full xml style OB header
# --- End of user config ---

#constants and list for icon list generating
image_file_prefix = (".png", ".svg", ".xpm")
image_cat_prefix = ("applications-", "accessories-dictionary", "accessories-text-editor","preferences-desktop.","audio-speakers") 
iconThemes=os.listdir(image_dir_base[0]+"/icons")
tmplst=[s for s in iconThemes if selected_theme in s]
selected_theme = iconThemes[0] if tmplst == [] else tmplst[0]
iconThemes.sort(key=str.lower)
#iconThemes = ("hicolor", "breeze", "Adwaita", "Papirus", "Tango")  #you can manually enter icon names here with your own sorting
iconThemes.remove(selected_theme)
iconThemes.remove('hicolor') if 'hicolor' in iconThemes else False
iconThemes.insert(0, selected_theme) if selected_theme != 'hicolor' else False
iconThemes.insert(0, "hicolor")
iconList=[]

#getting icons to lists for faster menu generate
def addIconsToList(List, theme): # skip to next icon theme if any icon couldn't found on current
	for path in reversed(image_dir_base):
		for prfx in prefixes:
			for size in iconSizes:
				tmp = path + "/icons/" + theme + "/" + size + "/" + prfx
				if theme == "breeze" or theme == "breeze-dark":
					tmp = path + "/icons/" + theme + "/" + prfx + "/" + size
				try:
					List.extend(tmp + "/" +  x for x in os.listdir(tmp) if x.lower().endswith(image_file_prefix))
				except IOError:
					continue
	return List

def which(program): #check if program exist
	def is_exe(fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
	fpath, fname = os.path.split(program)
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			exe_file = os.path.join(path, program)
			if is_exe(exe_file):
				return exe_file
	return None

class dtItem(object):
	def __init__(self, fName):
		self.fileName = fName
		self.Name = ""
		self.Comment = ""
		self.Exec = ""
		self.Terminal = None
		self.Type = ""
		self.Icon = ""
		self.Categories = ()

	def addName(self, data):
		self.Name = xescape(data)

	def addComment(self, data):
		self.Comment = data

	def addExec(self, data):
		if len(data) > 3 and data[-2] == '%': # get rid of filemanager arguments in dt files
			data = data[:-2].strip()
		self.Exec = data

	def addIcon(self, data):
		self.Icon = ""
		if image_cat_prefix == "":
			return
		image_dir = image_dir_base[0] + "/pixmaps/"
		di = data.strip()
		if len(di) < 3:
			#"Error in %s: Invalid or no icon '%s'" % (self.fileName,  di)
			return
		dix = di.find("/")      # is it a full path?
		if dix >= 0 and dix <= 2:    # yes, its a path (./path or ../path or /path ...)
			self.Icon = di
			return
		#else a short name like "myapp"
		tmp = glob.glob(image_dir + di + ".*")
		if len(tmp) == 0: #if there is not correct icon in pixmap, check for icon theme
			for theme in iconThemes:
				tmp=[s for s in iconList if di in s] #check program name in icon list
				if len(tmp) > 0:
					break # end loop if found
				else:
					addIconsToList(iconList, theme)
		if len(tmp) == 1 and tmp[0] != "/":
			self.Icon = tmp[0]
		if len(tmp) > 1: # if there are duplicated icons take one that has the shortest name
			temp=tmp[0] # assign first item to a temp path
			flen=len(temp.split("/")[-1]) # split filepath with "/" and take last element of list
			for fpath in tmp: # check filepath list for shortest filename
				tlen=len(fpath.split("/")[-1]) # split filepath with / and take last element of list
				if tlen<flen: # replace icon path with shorter filename path
					flen=tlen # reallocate shortest filename length
					temp=fpath # reallocate temp path
			self.Icon = temp
		return

	def addTerminal(self, data):
		if data == "True" or data == "true":
			self.Terminal = True
		else:
			self.Terminal = False

	def addType(self, data):
		self.Type = data

	def addCategories(self, data):
		self.Categories = data

def getCatIcon(cat):
	theme = selected_theme
	cat = image_cat_prefix[0] + cat.lower()
	#some category icons don't appear, for major icon themes, fixes for them
	if theme == "breeze" or theme == "breeze-dark":
		if cat == "applications-editors":
			cat = "applications-education-language"
		if cat == "applications-settings":
			cat = "applications-development"
	if theme != "Adwaita" and theme != "gnome":
		if cat == "applications-editors":
			cat = "applications-development"
	if theme == "Adwaita":
		if cat == "applications-multimedia":
			cat = "audio-speakers"
	if theme == "Adwaita" or theme == "Papirus" or theme == "gnome":
		if cat == "applications-editors":
			cat = "accessories-text-editor"
		if cat == "applications-settings":
			cat = "preferences-desktop"
		if cat == "applications-education":
			cat = "accessories-dictionary"
	if theme != "breeze" or theme != "breeze-dark":
		if cat == "applications-settings":
			cat = "preferences-desktop"
	if theme == "Tango":
		if cat == "applications-utilities":
			cat = "applications-accessories"
	tmp = [s for s in iconList if cat in s]
	if len(tmp) > 0:
		return tmp[0]
	return ""

def xescape(s):
	Rep = {"&":"&amp;", "<":"&lt;", ">":"&gt;",  "'":"&apos;", "\"":"&quot;"}
	for p in ("&", "<", ">",  "'","\""):
		sl = len(s); last = -1
		while last < sl:
			i = s.find(p,  last+1)
			if i < 0:
				done = True
				break
			last = i
			l = s[:i]
			r = s[i+1:]
			s = l + Rep[p] + r
	return s

def process_category(cat, curCats, aliases=group_aliases, appGroups=application_groups):
	# first process aliases
	if aliases.__contains__(cat):
		if aliases[cat] == "":
			return "" # ignore this one
		cat = aliases[cat]
	if cat in appGroups and cat not in curCats:  # valid categories only and no doublettes, please
		curCats.append(cat)
		return cat
	return ""

def process_dtfile(dtf,  catDict):  # process this file & extract relevant info
	active = False          # parse only after "[Desktop Entry]" line
	fh = open(dtf,  "r")
	lines = fh.readlines()
	this = dtItem(dtf)
	for l in lines:
		l = l.strip()
		if l == "[Desktop Entry]":
			active = True
			continue
		if active == False: # we don't care about licenses or other comments
			continue
		if l == None or len(l) < 1 or l[0] == '#':
			continue
		if l[0] == '[' and l !=  "[Desktop Entry]":
			active = False
			continue
		# else
		eqi = l.split('=',1)
		if len(eqi) < 2:
			print ("Error: Invalid .desktop line'" + l + "'")
			continue
		# Check what it is ...
		if eqi[0] == "Name":
			this.addName(eqi[1])
		elif eqi[0] == "Comment":
			this.addComment(eqi[1])
		elif eqi[0] == "Exec":
			# check if appExec command in desktop file is installed in system
			eqx=eqi[1].split(" ", 1)[0] 
			if which(eqx) == None: 
				return #don't add anything to menu if executable not found, goto next desktop file
			this.addExec(eqi[1]) # add appExec to list
		elif eqi[0] == "Icon":
			this.addIcon(eqi[1])
		elif eqi[0] == "Terminal":
			this.addTerminal(eqi[1])
		elif eqi[0] == "Type":
			if eqi[1] != "Application":
				continue
			this.addType(eqi[1])
		elif eqi[0] == "Categories":
			if eqi[1] == '':
				eqi[1] = "Other"
			if eqi[1][-1] == ';':
				eqi[1] = eqi[1][0:-1]
			cats = []
			dtCats = eqi[1].split(';')
			for cat in dtCats:
				result = process_category(cat,  cats)
			this.addCategories(cats)
		else:
			continue
	# add to catDict
	#this.dprint()
	if len(this.Categories) > 0:        # don't care about stuff w/o category
		for cat in this.Categories:
			catDict[cat].append(this)
			#catDict[cat].sort()  #python2 code, not working on py3

addIconsToList(iconList, selected_theme) # getting first icons for list
categoryDict = {}

if __name__ == "__main__":
	# init the application group dict (which will contain list of apps)
	application_groups=sorted(application_groups, key=str.lower)
	for appGroup in application_groups:
		categoryDict[appGroup] = []
	# now let's look  into the app dirs ...
	#changed desktop files processing loops to add flatpak applications and sorting
	dtFiles=[]
	for appDir in applications_dirs:
		appDir += "/*.desktop"
		dtFiles+=glob.glob(appDir)
	# process each .desktop file in dir
	for dtf in dtFiles:
		skipFlag = False
		for ifn in ignoreList:
			if dtf.find(ifn) >= 0:
				skipFlag = True
		if skipFlag == False:
			process_dtfile(dtf,  categoryDict)
	# now, generate jwm menu include
	if simpleOBheader == True:
		print ("<openbox_pipe_menu>") # magic header
	else:
		print ('<?xml version="1.0" encoding="UTF-8" ?><openbox_pipe_menu xmlns="http://openbox.org/"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  xsi:schemaLocation="http://openbox.org/" >')  #magic header
	appGroupLen = len(application_groups)
	for ag in range(appGroupLen):
		catList = categoryDict[application_groups[ag]]
		if len(catList) < 1:
			continue # don't create empty menus
		# sort list
		tmpList=[] #blank list to convert to tuple for sorting purpose
		for app in catList: 
			app.Name= ' '.join([word[0].upper()+word[1:] for word in app.Name.split(' ')]) # fancy way to capitalize first letters
			tmpList.append([app.Name, [app.Icon, app.Terminal, app.Exec]]) #creating a tuple to sort
		catList=sorted(tmpList, key = lambda x: x[0].lower()) #recreating catList with sorted tuple list
		#catList=sorted(tmpList, key=lambda (a,b): (a.lower(), b)) # sort with case ignore, py2 code, not working on py3
		# end of sort
		catStr = "<menu id=\"openbox-%s\" label=\"%s\" " % (application_groups[ag], application_groups[ag])
		tmp = getCatIcon(application_groups[ag])
		if tmp != "":
			catStr += "icon=\"%s\"" % tmp
		print (catStr + ">")
		for app in catList:
			progStr = "<item "
			progStr += "label=\"%s\" " % app[0] #add app's name
			if app[1][0] != "": #check if there is app icon
				progStr += "icon=\"%s\" " % app[1][0] #adding icons path
			progStr += "><action name=\"Execute\"><command><![CDATA["
			if app[1][1] == True:  #check if app run in terminal
				progStr += terminal_string + " "
			progStr += "%s]]></command></action></item>"  % app[1][2] #adding exec command
			print (progStr)
		print ("</menu>")
	print ("</openbox_pipe_menu>") # magic footer
	pass # done/debug break
