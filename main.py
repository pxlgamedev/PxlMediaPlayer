import vlc
import os
import sys
import copy
import codecs
import shutil
import urllib
import keyboard
from bearlibterminal import terminal
from configparser import ConfigParser

import user_interface as UI
import msvcrt

config = ConfigParser()
config.read('main.ini')

starting_path = config.get('innit', 'starting_path')
starting_drive = config.get('innit', 'starting_drive')

white_list = config.get('innit', 'white_list')

def save_watched_list():
	with open(starting_drive + starting_path + '/watched_list.txt', "w") as file:
		file.write(str(watched_list))

def load_watched_list():
	try:
		with open(starting_drive + starting_path + '/watched_list.txt', "r") as file:
			return eval(file.read())
	except:
		return {}

watched_list = load_watched_list()

class VLC:
	def __init__(self):
		self.Player = vlc.Instance('vlc --loop --global-key-play-pause="p" --key-toggle-fullscreen="enter" --sub-autodetect-file') #--width=500 --height=400 --video-x=290 --video-y=160 --no-video-deco --no-embedded-video --video-on-top vlc
		self.events = vlc.EventType
		self.t = 0
		self.l = 0
		self.p = 0

	def pos_callback(self, event):
		self.t = int(self.listPlayer.get_media_player().get_time() * 0.001)
		self.l = int(self.listPlayer.get_media_player().get_length() * 0.001)
		self.p = self.listPlayer.get_media_player().get_position()

	def pos_video(self, event):
		#print('video callback')
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
		self.listPlayer.get_media_player().video_set_key_input(False)
		self.listPlayer.get_media_player().video_set_mouse_input(True)
		self.manager = self.listPlayer.get_media_player().event_manager()
		self.start_callbacks()

	def start_callbacks(self):
		self.manager = self.listPlayer.get_media_player().event_manager()
		self.manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, self.pos_callback)
		self.manager.event_attach(vlc.EventType.MediaPlayerVout, self.pos_video)

	def play_all(self, path):
		self.mediaList = self.Player.media_list_new()
		songs = os.listdir(path)
		for s in songs:
			self.mediaList.add_media(self.Player.media_new(os.path.join(path,s)))
		self.listPlayer = self.Player.media_list_player_new()
		self.listPlayer.set_media_list(self.mediaList)
		self.start_callbacks()

	def add_to_playlist(self, path, file):
		self.mediaList.add_media(self.Player.media_new(os.path.join(path,file)))
		self.listPlayer.set_media_list(self.mediaList)

	def play_index(self, i):
		self.listPlayer.play_item_at_index(i)
		#self.listPlayer.get_media_player().set_video_title_display()
	def play(self):
		p = 0
		if self.p > 0:
			p = self.p
		self.listPlayer.play()
		name = self.listPlayer.get_media_player().get_media().get_mrl()
		if name in watched_list:
			p = watched_list[name]
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
		self.whitelist()
		self.listPlayer.stop()
	def set_volume(self, vol):
		self.listPlayer.get_media_player().audio_set_volume(vol)
	def get_name(self):
		name = self.listPlayer.get_media_player().get_media().get_mrl()
		name = name.split('/')[-1]
		name = name.replace('%20', ' ')
		name = name.replace('%27', '\'')
		return name

	def whitelist(self):
		global watched_list
		name = self.listPlayer.get_media_player().get_media().get_mrl()
		# white listing only movies and shows for the watched list
		for w in white_list:
			if w in name:
				watched_list[name] = self.p
		save_watched_list()

class MEDIAPLAYER:
	title = config.get('innit', 'title')
	window_width = config.get('innit', 'window_width')
	window_height = config.get('innit', 'window_height')
	full_screen = config.getboolean('innit', 'full_screen')
	tile_size = 16
	hotkeys = config.getboolean('innit', 'hotkeys')
	#################
	# System States #
	#################
	input_state = 'main'
	mouse_over = None
	scroll = 0
	current_playlist = []
	vol = 100
	theme = config.get('theme', 'current')
	def __init__(self):
		terminal.open()
		font = f'font: MegaFont.ttf, size={self.tile_size}'
		terminal.set(f"window: title={self.title}, size=70x40, cellsize=20x20, fullscreen=false; {font}")
		terminal.set("input.filter = keyboard+, mouse+")
		terminal.printf(25, 2, self.title)
		terminal.composition(terminal.TK_ON)
		rgb = UI.select_color('main').split(',')
		terminal.color(terminal.color_from_argb(255, int(rgb[0]), int(rgb[1]), int(rgb[2])))
		terminal.refresh()
		keyboard.add_hotkey(config.get('innit', 'key_toggle'), self.global_space, args=(' '))
		keyboard.add_hotkey('ctrl+shift+esc', self.global_space, args=('s'))
		keyboard.add_hotkey(config.get('innit', 'key_next'), self.global_space, args=('n'))
		keyboard.add_hotkey(config.get('innit', 'key_prev'), self.global_space, args=('b'))
		keyboard.add_hotkey(config.get('innit', 'key_pause'), self.global_space, args=('p'))
		keyboard.add_hotkey(config.get('innit', 'key_volup'), self.global_space, args=('u'))
		keyboard.add_hotkey(config.get('innit', 'key_voldn'), self.global_space, args=('m'))
		keyboard.add_hotkey(config.get('innit', 'key_rwnd'), self.global_space, args=('j'))
		keyboard.add_hotkey(config.get('innit', 'key_ffwd'), self.global_space, args=('k'))
		keyboard.add_hotkey(config.get('innit', 'key_stop'), self.global_space, args=('s'))
		keyboard.add_hotkey(config.get('innit', 'key_mark_watched'), self.global_space, args=('w'))
		self.start_main_loop()

	def global_space(self, key):
		if key == ' ':
			self.hotkeys = not self.hotkeys
		if self.hotkeys:
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
			if key == 'j':
				self.player.pan(-5)
			if key == 'k':
				self.player.pan(5)
			if key == 'n':
				self.player.next()
			if key == 'b':
				self.player.prev()
			if key == 'p':
				self.player.pause()
			if key == 's':
				self.player.stop()

	def start_main_loop(self):
		current_path = starting_path
		current_drive = starting_drive
		current_file = ''
		os.chdir(current_drive)
		self.player = None
		playlist = False
		playing = ''
		mute = False
		def play_new():
			if self.player != None:
				self.player.stop()
				self.player = None
			self.player = VLC()#vlc.MediaPlayer(current_drive + '//' + current_path + '/' + file)
			self.player.new_playlist()
			#vlc.video_set_key_input(self.player.listPlayer.get_media_player(), True)
			self.current_playlist = []
			self.player.add_to_playlist(current_drive + '//' + current_path + '/', current_file)
			self.current_playlist.append(current_drive + '//' + current_path + '/' + current_file)
			self.player.set_volume(self.vol)
			self.player.play()
			#sub = current_file[:-3:1] + 'srt'
			#sub = current_drive + '//' + current_path + '/' + sub
			#print(sub)
			#self.player.listPlayer.get_media_player().get_media().add_options("sub-file={}".format(sub))
		def play_add():
			self.player.add_to_playlist(current_drive + '//' + current_path + '/', current_file)
			self.current_playlist.append(current_drive + '//' + current_path + '/' + current_file)
			self.player.set_volume(self.vol)
			self.player.play()
		while True:
			key = None
			terminal.clear()
			if terminal.has_input():
				while terminal.has_input():
					key = terminal.read()
			if key == terminal.TK_CLOSE:
				save_watched_list()
				break
			if key == terminal.TK_RESIZED:
				pass
				#self.update_window()
			if self.input_state == 'main':
				#if self.player != None:
					#print(self.player.listPlayer.get_media_player().video_get_cursor())
				if key == terminal.TK_ESCAPE:
					if self.player != None:
						self.player.stop()
				if key == terminal.TK_SPACE:
					if self.player != None:
						self.player.pause()
					self.key = ''
				mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
				if UI.draw_window(1, 2, 68, 36):
					if key == 128:
						save_watched_list()
						break
				terminal.printf(25, 3, self.title)
				files = current_path.split('/')
				p = 10
				new_path = '/'
				for i in range(len(files)):
					if files[i] == '':
						continue
					terminal.printf(p, 1, '│')
					new_path = new_path + files[i] + '/'
					if UI.button_text(p+1, 1, files[i]) and key == 128:
						current_path = new_path
						break
					p += len(files[i]) + 1
				if UI.button_text(1, 1, 'Drive: ' + current_drive) and key == 128:
					if current_drive == 'C:':
						current_drive = 'D:'
						current_path = '/'
					else:
						current_drive = 'C:'
						current_path = '/'
					os.chdir(current_drive)
					self.scroll = 0
				file = self.list_dir(current_drive + current_path)
				if key == 128 and file != None:
					if '.' in file:
						current_file = file
						if playlist == False:
							play_new()
						else:
							play_add()
						#except:
							#print('failed to load:', file)
					elif current_path == '/':
						current_path = current_path + file
						self.scroll = 0
					else:
						current_path = current_path + '/' + file
						self.scroll = 0
				if current_path != '/' and UI.button_text(2, 3, '...Back') and key == 128:
					self.scroll = 0
					new_path = current_path.split('/')
					current_path = '/'.join(new_path[:-1:1])
					if current_path == '':
						current_path = '/'
				################
				# File Browser #
				################
				w = 1
				h = 4
				if mouse[1] >= h and mouse[1] < h + 25:
					if mouse[0] >= w and mouse[0] < w + 51:
						if key == terminal.TK_MOUSE_SCROLL:
							self.scroll+=terminal.state(terminal.TK_MOUSE_WHEEL)
				UI.draw_rect(w, h, 3, 25)
				UI.draw_rect(w + 2, h, 50, 25)
				if UI.button_text(w+1, h + 2, '⮝') and key == 128:
					self.scroll -= 10
				if UI.button_text(w+1, h + 4, '▲') and key == 128:
					self.scroll -= 1
				if UI.button_text(w+1, h + 20, '▼') and key == 128:
					self.scroll += 1
				if UI.button_text(w+1, h + 22, '⮟') and key == 128:
					self.scroll += 10
				if UI.button_text(w+3, h + 26, 'Play All') and key == 128:
					try:
						if self.player != None:
							self.player.stop()
							self.player = None
							continue
						self.current_playlist = []
						self.player = VLC()
						self.player.play_all(current_path)
						dir = os.listdir(current_path)
						for i in dir:
							file = i.split('/')[-1]
							self.current_playlist.append(current_drive + '//' + current_path + '/' + file)
						self.player.set_volume(self.vol)
						self.player.play()
					except:
						print('could not play dir', current_path)
				if playlist:
					if UI.button_text(w+19, h + 26, 'Selection: Add') and key == 128:
						playlist = False
				else:
					if UI.button_text(w+19, h + 26, 'Selection: Play') and key == 128:
						playlist = True
				###################
				# Playlist Window #
				###################
				w = 52
				h = 4
				UI.draw_rect(w, h, 17, 25)
				count = 0
				if self.current_playlist != []:
					for i in range(len(self.current_playlist)):
						file = self.current_playlist[i].split('/')[-1]
						count += 1
						if file == playing:
							terminal.printf(w+1, h+count, '[color=' + UI.select_color('selected') + ']' + self.trimmed(file, 17))
						else:
							if UI.button_text(w+1, h+count, self.trimmed(file, 13)) and key == 128:
								self.player.play_index(i)
				#################
				# Player Window #
				#################
				if self.player != None:
					w = 36
					h = 28
					if UI.draw_window(w+1, h+1, 30, 6) and key == 128:
						self.player.stop()
						self.player = None
						continue
					playing = self.trimmed(self.player.get_name(), 60)
					terminal.printf(5,h+8, playing)
					bar, pos = UI.time_bar(4, h+7, 63, self.player.p)
					if bar and key == 128:
						self.player.listPlayer.get_media_player().set_position(pos)
					UI.draw_rect(3, h+6, 64, 4)
					if mouse[1] >= h and mouse[1] < h + 6:
						if mouse[0] >= w and mouse[0] < w + 32:
							if key == terminal.TK_MOUSE_SCROLL:
								self.vol -= terminal.state(terminal.TK_MOUSE_WHEEL)
								if self.vol < 0:
									self.vol = 0
								elif self.vol > 200:
									self.vol = 200
								self.player.set_volume(self.vol)
					if UI.button_text(w + 2, h + 2, 'Play') and key == 128:
						self.player.play()
					if UI.button_text(w + 2, h + 5, 'Prev') and key == 128:
						self.player.prev()
					if UI.button_text(w + 9, h + 2, 'Pause') and key == 128:
						self.player.pause()
					if UI.button_text(w + 17, h+ 2, 'Stop') and key == 128:
						self.player.stop()
					if UI.button_text(w + 17, h+ 5, 'Next') and key == 128:
						self.player.next()
					if UI.button_text(w + 27, h+ 2, '▲') and key == 128:
						if self.vol < 200:
							self.vol += 5
						self.player.set_volume(vol)
					if UI.button_text(w + 27, h+ 4, '▼') and key == 128:
						if self.vol > 0:
							self.vol -= 5
						self.player.set_volume(self.vol)
					if UI.button_text(w + 9, h+ 5, 'Mute') and key == 128:
						mute = not mute
						if mute:
							self.player.set_volume(0)
						else:
							self.player.set_volume(self.vol)
					terminal.printf(w+25,h+3, str(self.vol))
					terminal.printf(w+23,h+5, str(self.player.t) +'/'+str(self.player.l))
			terminal.refresh()
		print('closing')

	def trimmed(self, text, length):
		if len(text) > length:
			text = text[:length:1]
		return text

	def list_dir(self, path):
		#self.mouse_over = None
		dir = os.listdir(path)
		file = None
		size = 23
		# blacklist non playable files
		file_list = []
		for i in dir:
			if '.srt' not in i and '.txt' not in i:
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
				if watched_list[rname] > 0.9:
					color = '[color=grey]'
				elif watched_list[rname] > 0.7:
					color = '[color=dark orange]'
				elif watched_list[rname] > 0.6:
					color = '[color=orange]'
				elif watched_list[rname] > 0.4:
					color = '[color=light orange]'
				elif watched_list[rname] > 0.2:
					color = '[color=dark yellow]'
				elif watched_list[rname] > 0.1:
					color = '[color=yellow]'
				elif watched_list[rname] > 0.05:
					color = '[color=lighter yellow]'
				else:
					watched_list.pop(rname, None)
			name = self.trimmed(file_list[i + self.scroll], 48)
			if UI.button_text(4, 5 + i, name, color=color):
				self.mouse_over = rname
				file = file_list[i + self.scroll]
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
