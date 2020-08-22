import os
import ast


from bearlibterminal import terminal
import user_interface as UI

def main_tabs(self, w, h, key):
	UI.draw_rect(w, h, 22, 3)
	if self.input_state != 'main':
		if UI.button_text(w+1, h+1, 'Files', self.select_color('selected')) and key == 128:
			self.input_state = 'main'
	else:
		terminal.printf(w+1, h+1, '[color=' + self.select_color('grey') + ']Files')
	if self.input_state != 'eq':
		if UI.button_text(w+9, h+1, 'EQ', self.select_color('selected')) and key == 128:
			self.input_state = 'eq'
	else:
		terminal.printf(w+9, h+1, '[color=grey]EQ')
	if self.input_state != 'theme':
		if UI.button_text(w+14, h+1, 'Themes', self.select_color('selected')) and key == 128:
			self.input_state = 'theme'
	else:
		terminal.printf(w+14, h+1, '[color=' + self.select_color('grey') + ']Themes', self.select_color('selected'))

def equalizer(self, w, h, eq_presets, user, key):
	current_eq = user.get('settings', 'eq')
	terminal.printf(w+22, h-1, 'Equalizer Settings')
	count = 3
	for i in eq_presets.keys():
		if UI.button_text(w + 4, h + count, i, self.select_color('selected')) and key == 128:
			self.eq = ast.literal_eval(eq_presets[i])
			current_eq = i
			user.set('settings', 'eq', i)
		count += 2
	for i in range(10):
		p = (self.eq[i] + 20) / 40
		UI.draw_rect(w+15 + i * 3, h + 2, 3, 22)
		bar, pos = UI.slider_v(w+16 + i * 3, h + 22, 20, p, self.select_color('timebar'))
		if bar and key == 128:
			val = pos * 40 - 20
			self.eq[i] = val
	if self.player != None:
		self.player.update_eq(self.eq)
	UI.draw_rect(w+48, h + 2, 3, 22)
	p = (self.vol / 2) * 0.01
	bar, pos = UI.slider_v(w+49, h + 22, 20, p, self.select_color('timebar'))
	if bar and key == 128:
		self.vol = int(pos * 200)
		if self.player != None:
			self.player.set_volume(self.vol)
	if UI.button_text(w + 20, h + 25, current_eq, self.select_color('selected')) and key == 128:
		terminal.clear_area(w + 20, h + 25, 15, 1)
		terminal.printf(w + 8, h + 25, 'Enter name:')
		terminal.printf(w + 25, h + 27, 'Press Enter')
		new_eq = terminal.read_str(w + 20, h + 25, current_eq, 15)[1]
		eq_presets[new_eq] = str(self.eq)
		user.set('eq', new_eq, str(self.eq))
		current_eq = new_eq
	if UI.button_text(w + 30, h + 27, 'reset', self.select_color('selected')) and key == 128:
		for i in eq.keys():
			self.eq[i] = 0
		current_eq = 'new preset'
	if UI.button_text(w + 18, h + 27, 'save', self.select_color('selected')) and key == 128:
		eq_presets[current_eq] = str(self.eq)
		user.set('eq', current_eq, str(self.eq))
	self.save_settings()
		#ast.literal_eval(user.get('eq', 'default'))

def themes(self, w, h, theme_presets, user, key):
	theme_presets = dict(user.items('theme'))
	terminal.printf(w +22, h-1, 'Theme Settings')
	themes = {}
	for i in theme_presets:
		themes[i] = ast.literal_eval(user.get('theme', i))
	count = 3
	current_theme = user.get('settings', 'theme')
	for i in themes.keys():
		if UI.button_text(w + 4, h + count, i, self.select_color('selected')) and key == 128:
			current_theme = i
			user.set('settings', 'theme', i)
		count += 2
	count = 3
	terminal.printf(w + 20, h + 4, '[color=' + self.select_color('main') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 15, h + 4, 'Main:', self.select_color('selected')) and key == 128:
		self.cur_color = 'main'
	terminal.printf(w + 39, h + 4, '[color=' + self.select_color('selected') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 30, h + 4, 'Selected:', self.select_color('selected')) and key == 128:
		self.cur_color = 'selected'
	terminal.printf(w + 20, h + 7, '[color=' + self.select_color('hud') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 15, h + 7, 'Hud:', self.select_color('selected')) and key == 128:
		self.cur_color = 'hud'
	terminal.printf(w + 39, h + 7, '[color=' + self.select_color('timebar') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 30, h + 7, 'Timebar:', self.select_color('selected')) and key == 128:
		self.cur_color = 'timebar'
	terminal.printf(w + 20, h + 10, '[color=' + self.select_color('grey') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 15, h + 10, 'Grey:', self.select_color('selected')) and key == 128:
		self.cur_color = 'grey'
	terminal.printf(w + 39, h + 10, '[color=' + self.select_color('close') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 30, h + 10, 'Close:', self.select_color('selected')) and key == 128:
		self.cur_color = 'close'
	new_pre = False
	if UI.button_text(w + 30, h + 27, 'New', self.select_color('selected')) and key == 128:
		new_pre = True
	if (UI.button_text(w + 20, h + 25, current_theme, self.select_color('selected')) and key == 128) or new_pre:
		terminal.clear_area(w + 20, h + 25, 15, 2)
		terminal.printf(w + 8, h + 25, 'Enter name:')
		terminal.printf(w + 25, h + 27, 'Press Enter')
		new_theme = terminal.read_str(w + 20, h + 25, current_theme, 15)[1]
		themes[new_theme] = themes[current_theme]
		user.set('settings', 'theme', current_theme)
		user.set('theme', new_theme, str(themes[current_theme]))
		current_theme = new_theme
	if UI.button_text(w + 18, h + 27, 'save', self.select_color('selected')) and key == 128:
		self.save_settings()
	terminal.printf(w + 12, h + 14, 'Select new color for ' + self.cur_color +':')
	swatch, color = UI.color_selector(w + 3, h + 16, 45, self.select_color(self.cur_color))
	if swatch and key == 128:
		themes[current_theme][self.cur_color] = str(color)
		user.set('theme', current_theme, str(themes[current_theme]))


def file_browser(self, w, h, key):
	################
	# File Browser #
	################
	# Scroll Bar
	UI.draw_rect(w, h, 3, 25)
	if UI.button_text(w+1, h + 2, '⮝', self.select_color('selected')) and key == 128:
		self.scroll -= 22
	if UI.button_text(w+1, h + 4, '▲', self.select_color('selected')) and key == 128:
		self.scroll -= 1
	if UI.button_text(w+1, h + 20, '▼', self.select_color('selected')) and key == 128:
		self.scroll += 1
	if UI.button_text(w+1, h + 22, '⮟', self.select_color('selected')) and key == 128:
		self.scroll += 22
	# Mouse scroll
	if self.mouse[1] >= h and self.mouse[1] < h + 25:
		if self.mouse[0] >= w and self.mouse[0] < w + 51:
			if key == terminal.TK_MOUSE_SCROLL:
				self.scroll+=terminal.state(terminal.TK_MOUSE_WHEEL)
	# Initiate file search
	files = self.current_path.split('/')
	p = 12
	new_path = '/'
	for i in range(len(files)):
		if files[i] == '':
			continue
		terminal.printf(p, 4, '│')
		new_path = new_path + files[i] + '/'
		if UI.button_text(p+1, 4, files[i], self.select_color('selected')) and key == 128:
			self.current_path = new_path
			break
		p += len(files[i]) + 1
	if UI.button_text(3, 4, 'Drive: ' + self.current_drive, self.select_color('selected')) and key == 128:
		if self.current_drive == 'C:':
			self.current_drive = 'D:'
			self.current_path = '/'
		else:
			self.current_drive = 'C:'
			self.current_path = '/'
		os.chdir(self.current_drive)
		self.scroll = 0
	file = self.list_dir(w, h, self.current_drive + self.current_path)
	if key == 128 and file != None:
		# Run a hyperlink file #
		if file[-6::1] == '.hyper':
			with open(self.current_drive + '//' + self.current_path + '/' + file, "r") as f:
				links = ast.literal_eval(f.read())
			for l in links:
				if self.playlist == False:
					play_new(l)
					break
				else:
					self.play_add(l)
		elif '.' in file:
			self.current_file = file
			if self.playlist == False:
				self.play_new()
			else:
				self.play_add()
		elif self.current_path == '/':
			self.current_path = self.current_path + file
			self.scroll = 0
		else:
			self.current_path = self.current_path + '/' + file
			self.scroll = 0
	'''
	if self.current_path != '/' and UI.button_text(2, 3, '...Back', self.select_color('selected')) and key == 128:
		self.scroll = 0
		new_path = self.current_path.split('/')
		self.current_path = '/'.join(new_path[:-1:1])
		if self.current_path == '':
			self.current_path = '/'
	'''
	if UI.button_text(w+3, h + 26, 'Play All', self.select_color('selected')) and key == 128:
		try:
			if self.player != None:
				self.player.stop()
				self.player = None
				key = None
			self.current_playlist = []
			self.player = VLC()
			self.player.play_all(self.current_path)
			dir = os.listdir(self.current_path)
			for i in dir:
				file = i.split('/')[-1]
				self.current_playlist.append(self.current_drive + '//' + self.current_path + '/' + file)
			self.player.set_volume(self.vol)
			self.player.play()
		except:
			print('could not play dir', self.current_path)
	if self.playlist:
		if UI.button_text(w+19, h + 26, 'Selection: Add', self.select_color('selected')) and key == 128:
			self.playlist = False
	else:
		if UI.button_text(w+19, h + 26, 'Selection: Play', self.select_color('selected')) and key == 128:
			self.playlist = True

def playlist(self, w, h, key):
	UI.draw_rect(w, h, 17, 25)
	count = 0
	if self.current_playlist != []:
		for i in range(len(self.current_playlist)):
			file = self.current_playlist[i].split('/')[-1]
			count += 1
			if file == self.playing:
				terminal.printf(w+1, h+count, '[color=' + self.select_color('selected') + ']' + self.trimmed(file, 15))
			else:
				if UI.button_text(w+1, h+count, self.trimmed(file, 13), self.select_color('selected')) and key == 128:
					self.player.play_index(i)

def player_ui(self, w, h, key):
	if UI.draw_window(w+1, h+1, 26, 7, self.select_color('hud'), self.select_color('close')) and key == 128:
		self.player.stop()
		self.player = None
		key = None
	if self.mouse[1] >= h and self.mouse[1] < h + 6:
		if self.mouse[0] >= w and self.mouse[0] < w + 32:
			if key == terminal.TK_MOUSE_SCROLL:
				self.vol -= terminal.state(terminal.TK_MOUSE_WHEEL)
				if self.vol < 0:
					self.vol = 0
				elif self.vol > 200:
					self.vol = 200
				self.player.set_volume(self.vol)
	if UI.button_text(w + 3, h + 5, '◄◄', self.select_color('selected')) and key == 128:
		self.player.prev()
	if UI.button_text(w + 8, h + 5, '➤', self.select_color('selected')) and key == 128:
		self.player.play()
	if UI.button_text(w + 11, h + 5, '||', self.select_color('selected')) and key == 128:
		self.player.pause()
	if UI.button_text(w + 15, h+ 5, '▓', self.select_color('selected')) and key == 128:
		self.player.stop()
	if UI.button_text(w + 19, h+ 5, '►►', self.select_color('selected')) and key == 128:
		self.player.next()
	if UI.button_text(w + 25, h+ 3, '▲', self.select_color('selected')) and key == 128:
		if self.vol < 200:
			self.vol += 5
		self.player.set_volume(vol)
	terminal.printf(w+23,h+4, str(self.vol))
	if UI.button_text(w + 25, h+ 5, '▼', self.select_color('selected')) and key == 128:
		if self.vol > 0:
			self.vol -= 5
		self.player.set_volume(self.vol)
	if UI.button_text(w + 16, h+ 3, 'Mute', self.select_color('selected')) and key == 128:
		self.mute = not self.mute
		if self.mute:
			self.player.set_volume(0)
		else:
			self.player.set_volume(self.vol)
	if UI.button_text(w + 10, h+ 3, 'Rep', self.select_color('selected')) and key == 128:
		pass
	if UI.button_text(w + 4, h+ 3, 'Shuf', self.select_color('selected')) and key == 128:
		pass

def track_title_ui(self, w, h, key):
	self.playing = self.trimmed(self.player.get_name(), 62)
	terminal.printf(5,h+8, self.playing)
	bar, pos = UI.slider_h(2, h+9, 66, self.player.p, self.select_color('timebar'))
	if bar and key == 128:
		self.player.listPlayer.get_media_player().set_position(pos)
	UI.draw_rect(1, h+7, 68, 4)
	# Time remaining from seconds
	t = str(int(self.player.t / 60)) + ':' + str(int(self.player.t % 60))
	l = str(int(self.player.l / 60)) + ':' + str(int(self.player.l % 60))
	terminal.printf(30,h+9, t + '/' + l)
