import os
import ast


from bearlibterminal import terminal
import user_interface as UI

def main_tabs(self, w, h, key):
	#UI.draw_panel(w, h, 22, 3, self.select_color('hud'))
	UI.draw_rect(w-1, h, 24, 3)
	if self.input_state != 'main':
		if UI.button_text(w+1, h+1, 'Files', self.select_color('selected')) and key == 128:
			self.input_state = 'main'
	else:
		terminal.printf(w+1, h+1, '[color=' + self.select_color('grey') + ']Files')
	if self.input_state != 'eq':
		if UI.button_text(w+8, h+1, 'EQ', self.select_color('selected')) and key == 128:
			self.input_state = 'eq'
	else:
		terminal.printf(w+8, h+1, '[color=grey]EQ')
	if self.input_state != 'theme':
		if UI.button_text(w+12, h+1, 'Themes', self.select_color('selected')) and key == 128:
			self.input_state = 'theme'
	else:
		terminal.printf(w+12, h+1, '[color=' + self.select_color('grey') + ']Themes', self.select_color('selected'))
	if self.input_state != 'settings':
		if UI.button_text(w+20, h+1, '☼', self.select_color('selected')) and key == 128:
			self.input_state = 'settings'
	else:
		terminal.printf(w+20, h+1, '[color=' + self.select_color('grey') + ']☼', self.select_color('selected'))

def file_browser(self, w, h, key, VLC):
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
	p = 5
	new_path = ''
	for i in range(len(files)):
		if files[i] == '':
			continue
		terminal.printf(p, 4, '│')
		new_path = new_path + '/' + files[i]
		if UI.button_text(p+1, 4, files[i], self.select_color('selected')) and key == 128:
			self.current_path = new_path
			break
		p += len(files[i]) + 1
	if UI.button_text(3, 4, self.current_drive, self.select_color('selected')) and key == 128:
		self.drop_down = 1 if self.drop_down != 1 else None
		key = None
	file = self.list_dir(w, h, self.current_drive + self.current_path)# if self.drop_down == None else None
	if self.drop_down == 1:
		pos = UI.drop_down_list(3, 5, self.current_drives, self.select_color('selected'), self.select_color('hud'))
		if pos != None and key == 128:
			self.current_drive = self.current_drives[pos]
			self.current_path = '/'
			os.chdir(self.current_drive)
			self.scroll = 0
			self.drop_down = None
	if key == 128 and file != None:
		# Run a hyperlink file #
		if file[-5::1] == '.hypr':
			with open(self.current_drive + '//' + self.current_path + '/' + file, "r") as f:
				links = ast.literal_eval(f.read())
			for l in links:
				if self.playlist == False:
					self.play_new(l)
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
	if key == 128:
		self.drop_down = None
	'''
	if self.current_path != '/' and UI.button_text(w+3, h+1, '...', self.select_color('selected')) and key == 128:
		self.scroll = 0
		new_path = self.current_path.split('/')
		self.current_path = '/'.join(new_path[:-1:1])
		if self.current_path == '':
			self.current_path = '/'
	'''
	if UI.button_box(w+3, h + 25, 'Play All', self.select_color('selected')) and key == 128:
		if self.player != None:
			self.player.stop()
			self.player = None
			key = None
		self.current_playlist = []
		self.player = VLC()
		dir = os.listdir(self.current_path)
		for i in dir:
			file = i.split('/')[-1]
			self.current_file = file
			self.play_add()
		self.player.set_volume(self.vol)
		self.player.play()
	if self.playlist:
		if UI.button_box(w+19, h + 25, 'Selection: Add', self.select_color('selected')) and key == 128:
			self.playlist = False
	else:
		if UI.button_box(w+19, h + 25, 'Selection: Play', self.select_color('selected')) and key == 128:
			self.playlist = True

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
	new_pre = False
	if UI.button_box(w + 29, h + 26, 'New', self.select_color('selected')) and key == 128:
		new_pre = True
	if (UI.button_text(w + 20, h + 25, current_eq, self.select_color('selected')) and key == 128) or new_pre:
		terminal.clear_area(w + 20, h + 25, 20, 4)
		UI.draw_panel(w+20, h+25, 20, 4, self.select_color('hud'))
		terminal.printf(w + 8, h + 25, 'Enter name:')
		terminal.printf(w + 25, h + 27, 'Press Enter')
		UI.draw_rect(w+19, h+24, 12, 3)
		new_eq = terminal.read_str(w + 20, h + 25, current_eq, 10)[1]
		eq_presets[new_eq] = str(self.eq)
		user.set('eq', new_eq, str(self.eq))
		current_eq = new_eq
	if UI.button_box(w + 23, h + 26, 'Reset', self.select_color('selected')) and key == 128:
		for i in self.eq.keys():
			self.eq[i] = 0
	if UI.button_box(w + 18, h + 26, 'Save', self.select_color('selected')) and key == 128:
		eq_presets[current_eq] = str(self.eq)
		user.set('eq', current_eq, str(self.eq))
	if current_eq != 'default' and (UI.button_box(w + 33, h + 26, 'Delete', self.select_color('selected')) and key == 128):
		self.eq = ast.literal_eval(eq_presets['default'])
		current_eq = 'default'
		user.set('settings', 'eq', 'default')
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
	terminal.printf(w + 20, h + 2, '[color=' + self.select_color('main') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 15, h + 2, 'Main:', self.select_color('selected')) and key == 128:
		self.cur_color = 'main'
	terminal.printf(w + 39, h + 2, '[color=' + self.select_color('selected') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 30, h + 2, 'Selected:', self.select_color('selected')) and key == 128:
		self.cur_color = 'selected'
	terminal.printf(w + 20, h + 5, '[color=' + self.select_color('hud') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 15, h + 5, 'Hud:', self.select_color('selected')) and key == 128:
		self.cur_color = 'hud'
	terminal.printf(w + 39, h + 5, '[color=' + self.select_color('timebar') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 30, h + 5, 'Timebar:', self.select_color('selected')) and key == 128:
		self.cur_color = 'timebar'
	terminal.printf(w + 20, h + 8, '[color=' + self.select_color('grey') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 15, h + 8, 'Grey:', self.select_color('selected')) and key == 128:
		self.cur_color = 'grey'
	terminal.printf(w + 39, h + 8, '[color=' + self.select_color('close') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 30, h + 8, 'Close:', self.select_color('selected')) and key == 128:
		self.cur_color = 'close'
	terminal.printf(w + 20, h + 11, '[color=' + self.select_color('mark') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 15, h + 11, 'Mark:', self.select_color('selected')) and key == 128:
		self.cur_color = 'mark'
	terminal.printf(w + 39, h + 11, '[color=' + self.select_color('watching') + ']▓▓▓▓▓▓▓▓')
	if UI.button_text(w + 30, h + 11, 'Watching:', self.select_color('selected')) and key == 128:
		self.cur_color = 'watching'
	new_pre = False
	if UI.button_box(w + 29, h + 26, 'New', self.select_color('selected')) and key == 128:
		new_pre = True
	if (UI.button_text(w + 20, h + 25, current_theme, self.select_color('selected')) and key == 128) or new_pre:
		terminal.clear_area(w + 20, h + 25, 20, 4)
		UI.draw_panel(w+20, h+25, 20, 4, self.select_color('hud'))
		terminal.printf(w + 8, h + 25, 'Enter name:')
		terminal.printf(w + 25, h + 27, 'Press Enter')
		UI.draw_rect(w+19, h+24, 12, 3)
		new_theme = terminal.read_str(w + 20, h + 25, current_theme, 10)[1]
		themes[new_theme] = themes[current_theme]
		user.set('settings', 'theme', current_theme)
		user.set('theme', new_theme, str(themes[current_theme]))
		current_theme = new_theme
	if UI.button_box(w + 18, h + 26, 'save', self.select_color('selected')) and key == 128:
		self.save_settings()
	if current_theme != 'default' and (UI.button_box(w + 33, h + 26, 'Delete', self.select_color('selected')) and key == 128):
		self.eq = themes['default']
		current_theme = 'default'
		user.set('settings', 'theme', 'default')
	terminal.printf(w + 20, h + 14, 'Select new color for ' + self.cur_color +':')
	swatch, color = UI.color_selector(w + 3, h + 16, 45, self.select_color(self.cur_color))
	if swatch and key == 128:
		themes[current_theme][self.cur_color] = str(color)
		user.set('theme', current_theme, str(themes[current_theme]))

def settings(self, w, h, user, key):
	if UI.button_box(w + 18, h + 26, 'Text Entry', self.select_color('selected')) and key == 128:
		s = ''
		text_area = ['']
		'''
		word wrap each string in the list, and then join the list with '\n'
		'''
		width = 45
		height = 22
		cursor_pos = 0
		while True:
			terminal.clear_area(w+3, h+1, width, height+1)
			k = terminal.read()
			mouse = (terminal.state(terminal.TK_MOUSE_X), terminal.state(terminal.TK_MOUSE_Y))
			if k == terminal.TK_ESCAPE or k == terminal.TK_CLOSE:
				break
			elif k == terminal.TK_RETURN:
				if len(s) > cursor_pos:
					prev = s[:cursor_pos:1]
					next = s[cursor_pos::1]
					s = prev + ' \n ' + next
				else:
					s = s + ' \n '
				cursor_pos += 4
			elif k == terminal.TK_BACKSPACE:
				if len(s) > cursor_pos:
					s = s[:cursor_pos - 1:1] + s[cursor_pos::1]
				else:
					s = s[:-1:1]
				cursor_pos -= 1
			elif terminal.check(terminal.TK_WCHAR): # and len(s) < width:
				s = s[:cursor_pos:1] + chr(terminal.state(terminal.TK_WCHAR)) + s[cursor_pos::1]
				cursor_pos += 1
				#text_area[-1] = text_area[-1] +
			text = []
			new_line = ''
			for word in s.split(' '):
				if '\n' in word:
					text.append(new_line)
					new_line = ''
				elif len(new_line) + len(word) + 1 < width:
					new_line = new_line + ' ' + word
				else:
					text.append(new_line)
					new_line = word
			text.append(new_line)
			print(s)
			if (mouse[1] <= h + height and mouse[1] >= h) and (mouse[0] <= w + width and mouse[0] >= w) and k == terminal.TK_MOUSE_LEFT:
				index = max(0, mouse[1] - h - 1)
				pos = max(0, mouse[0] - w - 3)
				if index < len(text):
					if pos < len(text[index]):
						new_pos = 0
						for i in range(0, index):
							new_pos += len(text[i])
						new_pos += pos
						cursor_pos = new_pos
						print(text[index][pos])
					else:
						print(text[index][len(text[index]) -1])
			if len(text) > 0:
				text = '\n'.join(text[-height::1])
			terminal.printf(w+3, h+1, text + '▓')
			terminal.refresh()

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
	if UI.button_box(w + 16, h+ 2, 'Mute', self.select_color('selected')) and key == 128:
		self.mute = not self.mute
		if self.mute:
			self.player.set_volume(0)
		else:
			self.player.set_volume(self.vol)
	if UI.button_box(w + 10, h+ 2, 'Rep', self.select_color('selected')) and key == 128:
		pass
	if UI.button_box(w + 4, h+ 2, 'Shuf', self.select_color('selected')) and key == 128:
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
