import os
import sys
import vlc
import ast
import copy
import time
import msvcrt
import codecs
import shutil
import urllib
import keyboard

import ctypes
from ctypes import wintypes

from bearlibterminal import terminal
from configparser import ConfigParser
'''
#from Xlib.display import Display
def printWindowHierrarchy(window, indent):
    children = window.query_tree().children
    for w in children:
        print(indent, w.get_wm_class())
        printWindowHierrarchy(w, indent+'-')
'''
def get_current_win():
	user32 = ctypes.windll.user32
	h_wnd = user32.GetForegroundWindow()
	pid = wintypes.DWORD()
	user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
	return pid.value

config = ConfigParser()
config.read('main.ini')

dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]
starting_drive = config.get('innit', 'starting_drive') if config.get('innit', 'starting_drive') in drives else drives[0]
starting_path = config.get('innit', 'starting_path') if os.path.exists( starting_drive + '/' + config.get('innit', 'starting_path')) else '/'

# Folders which will be tracked for the watched_list
white_list = ast.literal_eval(config.get('innit', 'white_list'))
file_types = ast.literal_eval(config.get('innit', 'file_types'))

# User settings
user = ConfigParser()
header = '''
#########################################
# User Config File for PxL Media PLayer #
#        MODIFY AT YOUR OWN RISK        #
#########################################
\n'''
owd = os.getcwd()

try:
	user.read('user_settings.ini')
	eq_presets = dict(user.items('eq'))
	theme_presets = dict(user.items('theme'))
except:
	new = config.get('eq', 'default')
	def_theme = dict(user.items('default'))
	user.add_section('settings')
	user.add_section('eq')
	user.add_section('theme')
	user.set('eq', 'default', new)
	user.set('theme', 'default', str(def_theme))
	eq_presets = dict(user.items('eq'))
	theme_presets = dict(user.items('theme'))
	with open('user_settings.ini', "w") as file:
		user.write(file)

import user_interface as UI
import modules as MOD

def save_watched_list():
	#curDir = os.getcwd() # save current directory
	#print(curDir)
	#os.chdir(owd) # return to working dir
	with open('watched_list.txt', "w") as file:
		file.write(str(watched_list))
	#os.chdir(curDir) # change back

def load_watched_list():
	#curDir = os.getcwd() # save current directory
	#os.chdir(owd) # return to working dir
	try:
		with open('watched_list.txt', "r") as file:
			return ast.literal_eval(file.read())
	except:
		print('No watched_list.txt found')
		return {}
	#os.chdir(curDir) # change back

# Dict of files and their last stop time
watched_list = load_watched_list()

# The player object for accessing python-VLC
class VLC:
	def __init__(self):
		self.Player = vlc.Instance('vlc --video-title=Player --loop --key-play-pause=space --key-toggle-fullscreen=enter --sub-autodetect-file') #--width=500 --height=400 --video-x=290 --video-y=160 --no-video-deco --no-embedded-video --video-on-top vlc
		self.events = vlc.EventType
		self.eq = vlc.libvlc_audio_equalizer_new()
		self.t = 0
		self.l = 0
		self.p = 0
		self.new_playlist()

	def update_eq(self, eq):
		for i in range(10):
			n = vlc.libvlc_audio_equalizer_set_amp_at_index(self.eq, eq[i], i)
			if n == -1:
				print('failed', i)
		try:
			self.listPlayer.get_media_player().set_equalizer(self.eq)
		except:
			print('seting eq failed')

	def pos_callback(self, event):
		self.t = int(self.listPlayer.get_media_player().get_time() * 0.001)
		self.l = int(self.listPlayer.get_media_player().get_length() * 0.001)
		self.p = self.listPlayer.get_media_player().get_position()
		self.whitelist()

	def pos_video(self, event):
		# Autoset Subtitle Track #
		spu_count = self.listPlayer.get_media_player().video_get_spu_count()
		if spu_count > 1:
			print('subs:', (self.listPlayer.get_media_player().video_set_spu(2) == 0))
		#spu = vlc.libvlc_video_get_spu_description(self.listPlayer.get_media_player())
		#vlc.libvlc_track_description_list_release(spu)
		#print(self.listPlayer.get_media_player().get_media().tracks_get())

	def new_playlist(self):
		self.mediaList = self.Player.media_list_new()
		self.listPlayer = self.Player.media_list_player_new()
		self.listPlayer.set_media_list(self.mediaList)
		self.listPlayer.get_media_player().set_equalizer(self.eq)
		self.listPlayer.get_media_player().video_set_key_input(True)
		#self.listPlayer.get_media_player().video_set_mouse_input(True)
		self.manager = self.listPlayer.get_media_player().event_manager()
		self.start_callbacks()

	def start_callbacks(self):
		self.manager = self.listPlayer.get_media_player().event_manager()
		self.manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, self.pos_callback)
		self.manager.event_attach(vlc.EventType.MediaPlayerVout, self.pos_video)

	def add_to_playlist(self, path, file):
		self.mediaList.add_media(self.Player.media_new(os.path.join(path,file)))
		self.listPlayer.set_media_list(self.mediaList)

	def play_index(self, i):
		self.listPlayer.play_item_at_index(i)
		#self.listPlayer.get_media_player().set_video_title_display()
	def play(self):
		p = None
		#self.listPlayer.get_media_player().set_xwindow(get_current_win())
		self.listPlayer.play()
		name = self.listPlayer.get_media_player().get_media().get_mrl()
		if name in watched_list:
			p = watched_list[name]
		if p != None:
			self.listPlayer.get_media_player().set_position(p)

	def pan(self, t):
		c = self.listPlayer.get_media_player().get_time()
		c += t * 1000
		self.listPlayer.get_media_player().set_time(c)
	def next(self):
		self.listPlayer.next()
	def pause(self):
		self.listPlayer.pause()
	def prev(self):
		self.listPlayer.previous()
	def stop(self):
		self.listPlayer.stop()
		save_watched_list()
	def set_volume(self, vol):
		self.listPlayer.get_media_player().audio_set_volume(vol)
	def get_name(self):
		name = self.listPlayer.get_media_player().get_media().get_mrl()
		name = name.split('/')[-1]
		name = name.replace('%20', ' ')
		name = name.replace('%27', '\'')
		return name

	def fullscreen(self):
		f = not vlc.libvlc_get_fullscreen(self.listPlayer.get_media_player())
		vlc.libvlc_set_fullscreen(self.listPlayer.get_media_player(), f)

	def whitelist(self):
		global watched_list
		name = self.listPlayer.get_media_player().get_media().get_mrl()
		# white listing only movies and shows for the watched list
		for w in white_list:
			if w in name:
				watched_list[name] = self.p
		save_watched_list()

class MEDIAPLAYER:
	###############
	# Configurable #
	###############
	title = config.get('innit', 'title')
	theme = config.get('theme', 'current')
	hotkeys = config.getboolean('innit', 'hotkeys')
	tile_size = 16
	vol = 100
	#################
	# System States #
	#################
	input_state = 'main'
	drop_down = None
	mouse_over = None
	scroll = 0
	# Player States #
	current_playlist = []
	current_path = starting_path
	current_drives = drives
	current_drive = starting_drive
	current_file = ''
	playing = ''
	playlist = False
	mute = False
	try:
		eq = ast.literal_eval(user.get('eq', user.get('settings', 'eq')))
	except:
		eq = ast.literal_eval(user.get('eq', 'default'))
	try:
		th = ast.literal_eval(user.get('theme', user.get('settings', 'theme')))
	except:
		th = ast.literal_eval(user.get('theme', 'default'))
	def __init__(self):
		#####################################
		# Initialize BearLibTerminal Window #
		#####################################
		terminal.open()
		font = f'font: MegaFont.ttf, size={self.tile_size}'
		terminal.set(f"window: title={self.title}; {font}")
		terminal.set("input.filter = keyboard+, mouse+")
		terminal.printf(25, 2, self.title)
		terminal.composition(terminal.TK_ON)
		terminal.refresh()
		'''
		display = Display()
		root = display.screen().root
		printWindowHierrarchy(root, '-')
		'''
		self.window_id = get_current_win()
		###################################################################
		# Global Hotkeys using the keyboard module as a low level wrapper #
		###################################################################
		keyboard.add_hotkey(config.get('innit', 'key_toggle'), self.global_hotkey, args=(' '))
		keyboard.add_hotkey('ctrl+shift+esc', self.global_hotkey, args=('s'))
		keyboard.add_hotkey(config.get('innit', 'key_next'), self.global_hotkey, args=('n'))
		keyboard.add_hotkey(config.get('innit', 'key_prev'), self.global_hotkey, args=('b'))
		keyboard.add_hotkey(config.get('innit', 'key_pause'), self.global_hotkey, args=('p'))
		keyboard.add_hotkey(config.get('innit', 'key_volup'), self.global_hotkey, args=('u'))
		keyboard.add_hotkey(config.get('innit', 'key_voldn'), self.global_hotkey, args=('m'))
		keyboard.add_hotkey(config.get('innit', 'key_stop'), self.global_hotkey, args=('s'))
		keyboard.add_hotkey(config.get('innit', 'key_mark_watched'), self.global_hotkey, args=('w'))
		# these keys only work when the program is in focus
		keyboard.add_hotkey('enter', self.global_hotkey, args=('f'))
		keyboard.add_hotkey('space', self.global_hotkey, args=(' '))
		keyboard.add_hotkey('esc', self.global_hotkey, args=('q'))
		keyboard.add_hotkey('left', self.global_hotkey, args=('4'))
		keyboard.add_hotkey('right', self.global_hotkey, args=('6'))
		keyboard.add_hotkey('up', self.global_hotkey, args=('8'))
		keyboard.add_hotkey('down', self.global_hotkey, args=('2'))
		self.start_main_loop()

	def global_hotkey(self, key):
		# Workaround: Could not get functional controls on the popup video window from python-vlc
		# Low level global hotkey reader only works when the Media Player or it's popup video are in focus
		if self.window_id == get_current_win():
			if self.player != None:
				if key == ' ':
					self.player.pause()
				if key == 'f':
					self.player.fullscreen()
				if key == 'q':
					self.player.stop()
				if key == '4':
					self.player.pan(-5)
				if key == '6':
					self.player.pan(5)
				if key == '8':
					self.vol += 5
					if self.vol > 200:
						self.vol = 200
					self.player.set_volume(self.vol)
				if key == '2':
					self.player.set_volume(self.vol)
					self.vol -= 5
					if self.vol < 0:
						self.vol = 0
		# Regular global hotkeys from the ini file
		if self.hotkeys and self.player != None:
			if key == 'e':
				pass
			if key == 'w' and self.mouse_over != None:
				global watched_list
				watched_list[self.mouse_over] = 0.99
			if key == 'u':
				self.vol += 5
				if self.vol > 200:
					self.vol = 200
				self.player.set_volume(self.vol)
			if key == 'm':
				self.player.set_volume(self.vol)
				self.vol -= 5
				if self.vol < 0:
					self.vol = 0
			if key == 'n':
				self.player.next()
			if key == 'b':
				self.player.prev()
			if key == 'p':
				self.player.pause()
			if key == 's':
				self.player.stop()

	def select_color(self, string):
		theme = user.get('settings', 'theme')
		t = ast.literal_eval(user.get('theme', theme))
		c = t[string]
		#c = config.get('default', string)
		return c

	def save_settings(self):
		curDir = os.getcwd() # save current directory
		os.chdir(owd) # return to working dir
		with open('user_settings.ini', 'w') as configfile:
			configfile.write(header)
			user.write(configfile)
		os.chdir(curDir) # change back

	def play_new(self, link=None):
		if self.player != None:
			self.player.stop()
			self.player = None
		self.player = VLC()
		self.player.new_playlist()
		self.current_playlist = []
		if link != None:
			print(link)
			self.player.add_to_playlist('', link)
			self.current_playlist.append(link)
		else:
			self.player.add_to_playlist(self.current_drive + '//' + self.current_path + '/', self.current_file)
			self.current_playlist.append(self.current_drive + '//' + self.current_path + '/' + self.current_file)
		self.player.set_volume(self.vol)
		self.player.update_eq(self.eq)
		self.player.play()
		#self.player.listPlayer.get_media_player().get_media().add_options("sub-file={}".format(sub))
	def play_add(self, link=None):
		if '.' in self.current_file:
			if link != None:
				self.player.add_to_playlist('', link)
				self.current_playlist.append(link)
			elif self.current_file[-4::1] in file_types or self.current_file[-3::1] in file_types or self.current_file[-2::1] in file_types:
				self.player.add_to_playlist(self.current_drive + '//' + self.current_path + '/', self.current_file)
				self.current_playlist.append(self.current_drive + '//' + self.current_path + '/' + self.current_file)
			self.player.set_volume(self.vol)
			self.player.update_eq(self.eq)
			self.player.play()

	def start_main_loop(self):
		os.chdir(self.current_drive)
		self.player = None
		self.mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
		self.cur_color = 'main'
		while True:
			key = None
			self.mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
			terminal.clear()
			rgb = self.select_color('main').split(',')
			terminal.color(terminal.color_from_argb(255, int(rgb[0]), int(rgb[1]), int(rgb[2])))
			if terminal.has_input():
				while terminal.has_input():
					key = terminal.read()
			if key == terminal.TK_CLOSE:
				save_watched_list()
				break
			if key == terminal.TK_RESIZED:
				pass
			######################
			# Music Player Title #
			######################
			terminal.printf(28, 1, self.title)
			####################
			# Draw Main Window #
			# X Closes Program #
			####################
			if UI.draw_window(1, 3, 68, 36, self.select_color('hud'), self.select_color('close')) and key == 128:
				save_watched_list()
				break
			if self.input_state in ['main', 'eq', 'theme', 'settings']:
				#if self.player != None:
					#print(self.player.listPlayer.get_media_player().video_get_cursor())
				if key == terminal.TK_ESCAPE:
					if self.player != None:
						self.player.stop()
				if key == terminal.TK_SPACE or key == terminal.TK_P:
					if self.player != None:
						self.player.pause()
					self.key = ''
				################
				# Tab Switcher #
				################
				w = 2
				h = 1
				MOD.main_tabs(self, w, h, key)
				###############
				# Main window #
				###############
				w = 1
				h = 5
				UI.draw_rect(w + 2, h, 50, 25)
				if self.input_state == 'main':
					MOD.file_browser(self, w, h, key, VLC)
				elif self.input_state == 'eq':
					MOD.equalizer(self, w, h, eq_presets, user, key)
				elif self.input_state == 'theme':
					MOD.themes(self, w, h, theme_presets, user, key)
				elif self.input_state == 'settings':
					MOD.settings(self, w, h, user, key)
				###################
				# Playlist Window #
				###################
				w = 52
				h = 5
				MOD.playlist(self, w, h, key)
				#################
				# Player Window #
				#################
				if self.player != None:
					w = 42
					h = 28
					###############
					# Track Title #
					###############
					MOD.track_title_ui(self, w, h, key)
					MOD.player_ui(self, w, h, key)
			terminal.refresh()
		print('closing')

	def trimmed(self, text, length):
		if len(text) > length:
			text = text[:length:1]
		return text

	def list_dir(self, w, h, path):
		global watched_list
		#self.mouse_over = None
		curDir =os.getcwd().replace('\\', '/')
		if curDir != path:
			os.chdir(path)
			for n in white_list:
				if n in path:
					watched_list = load_watched_list()
					if watched_list == {}:
						watched_list = load_watched_list()
					break
		dir = os.listdir(path)
		file = None
		size = 23
		# blacklist non playable files
		file_list = []
		for i in dir:
			if '.' in i:
				if i[-4::1] in file_types or i[-3::1] in file_types or i[-2::1] in file_types:
					file_list.append(i)
			else:
				file_list.append(i)
		if self.scroll >= len(file_list) - size:
			if len(file_list) - size <= 0:
				self.scroll = 0
			else:
				self.scroll = len(file_list) - size
		elif self.scroll < 0:
			self.scroll = 0
		for i in range(len(file_list[self.scroll::1])):
			if i >= size:
				break
			rname = file_list[i + self.scroll]
			m = vlc.Media(path + '/' + rname)
			rname = m.get_mrl()
			color = ''
			# color code the watch list
			if rname in watched_list:
				if watched_list[rname] > 0.95:
					color = '[color=' + self.select_color('grey') + ']'
				elif watched_list[rname] > 0.7:
					color = '[color=' + self.select_color('watching') + ']'
				elif watched_list[rname] > 0.6:
					color = '[color=' + self.select_color('watching') + ']'
				elif watched_list[rname] > 0.4:
					color = '[color=' + self.select_color('watching') + ']'
				elif watched_list[rname] > 0.2:
					color = '[color=' + self.select_color('watching') + ']'
				elif watched_list[rname] > 0.1:
					color = '[color=' + self.select_color('mark') + ']'
				elif watched_list[rname] > 0.05:
					color = '[color=' + self.select_color('mark') + ']'
				else:
					watched_list.pop(rname, None)
			name = self.trimmed(file_list[i + self.scroll], 48)
			if self.drop_down == None and UI.button_text(w+3, h+1 + i, name, self.select_color('selected'), bg=color):
				self.mouse_over = rname
				file = file_list[i + self.scroll]
			else:
				terminal.printf(w+3, h+1 + i, color + name)
		return file

if __name__ == '__main__':
	profile_code = False
	if profile_code:
		import cProfile
		import pstats

		profile = cProfile.Profile()
		try:
			profile.runcall(MEDIAPLAYER)
		finally:
			stats = pstats.Stats(profile)
			stats.strip_dirs()
			stats.sort_stats("time")
			stats.print_stats(10)
	else:
		mediaplayer = MEDIAPLAYER()

'''
@ Issues
eq does not load until tab opened

@ TODO

screen lock

self contained playlist control

settings window

'''
