#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
# -*- tabstop: 4 -*-

'''
Simple links exchanget for teachers messages in Librus framework
'''

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango #, Gladeui, Gio
from os import path as ph
H = ph.expanduser('~') # Home dir
hh = lambda s: s.replace(H, '~')
from sys import stdout as sto
_p = lambda _str: sto.write(hh(str(_str)))
debug = (False, True)[1]
def _d(_str):
	if debug: _p(_str)

txtTypes = 'Input Output'.split()
actions ='Parse Clear Quit'.split()

import re
reMushLink = re.compile(r'https://liblink.pl/(?P<link_code>\w+)', re.U)

from urllib import request as ulrq

class LibruScar_UI:
	def __init__(ui):
		ui.uiInit()

	uiEnter = lambda ui: Gtk.main()
	uiQuit = lambda ui: Gtk.main_quit()

	def uiInit(ui):
		ui.runpath = ph.dirname(ph.realpath(__file__))
		screen = Gdk.Screen.get_default()
		gtk_provider = Gtk.CssProvider()
		gtk_context = Gtk.StyleContext()
		gtk_context.add_provider_for_screen(screen, gtk_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		ui.bld = Gtk.Builder()
		ui.bld.add_from_file(ph.join(ph.dirname(ph.abspath(__file__)), 'libruSca.ui'))
		ui.mainWindow = ui.bld.get_object('mainWindow')

		for txtType in txtTypes:
			ctrl_id = "txt%s" % txtType
			setattr(ui, ctrl_id, ui.bld.get_object(ctrl_id))

		ui.mainWindow.show_all()
		ui.mainWindow.set_keep_above(True)

	def set_text(ui, txv, txt):
		txv.get_buffer().set_text(txt)

	clear_text = lambda ui, txv: ui.set_text(txv, '')

	def get_text(ui, txv):
		tBuff = txv.get_buffer()
		return tBuff.get_text(tBuff.get_start_iter(), tBuff.get_end_iter(), False)

	def _p(ui, txv, txt):
		buff = txv.get_buffer()
		end = buff.get_end_iter()
		buff.insert(end, text)
		del(end)

class LibruScar:
	def __init__(mn):
		mn.uiInit()
		mn.appStart()

	def uiInit(mn):
		ui = mn.ui = LibruScar_UI()
		ui.mainWindow.connect("destroy", lambda w: mn.appQuit())
		handlers = {}
		for hn in actions:
			handlers['do_'+hn] = getattr(mn, 'app'+hn)
		ui.bld.connect_signals(handlers)

	def appAskLibLink(mn, link_code):
		from urllib import request as ulrq
		from lxml import html as ht
		response = None
		request = ulrq.urlopen("https://liblink.pl/%s" % link_code)
		if request.code == 200:
			response = request.readlines()
		request.close()
		if response:
			html = ''.join(map(lambda s:s.decode('utf-8'), response))
			tree = ht.fromstring(html)
			dest_urls = tree.xpath('//span[@style="color: #646464;"]/text()')
			if dest_urls:
				return dest_urls[0]
		return ''

	def appParse(mn, w):
		ui = mn.ui
		txt_in = ui.get_text(ui.txtInput)
		txt_out = ''
		for line in txt_in.splitlines():
			slices = []
			tmpline = line.lstrip()
			lmatch = reMushLink.search(tmpline)
			if not(lmatch):
				txt_out += tmpline+'\n'
				continue
			while tmpline:
				if lmatch:
					srchB, srchE = lmatch.span()
					txt_out += tmpline[:srchB]
					askLnk = mn.appAskLibLink(lmatch.group('link_code'))
					if askLnk:
						txt_out += askLnk
					else: # Internet request timeout or whatever, leave in oryginal
						txt_out += tmpline[srchB:srchE]
					tmpline = tmpline[srchE:]
					lmatch = reMushLink.search(tmpline)
					if not(lmatch):
						txt_out += tmpline
						break
			txt_out += '\n'
		ui.set_text(ui.txtOutput, txt_out)


	def appClear(mn, w):
		ui = mn.ui
		for txv in map(lambda ctrl_id: getattr(ui, "txt"+ctrl_id), txtTypes):
			txv.get_buffer().set_text('')

	def appStart(mn):
		mn.ui.uiEnter()

	def appQuit(mn, *w):
		mn.ui.uiQuit()

# Entry point
if __name__ == "__main__":
	LibruScar()
