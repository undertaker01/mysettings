from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
#from Components.Pixmap import Pixmap
#from enigma import ePicLoad
import gettext, base64, os, time, glob, urllib2
from os import environ, listdir, remove, rename, system, popen
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from boxbranding import *
from enigma import eEPGCache, eDVBDB

plugin='[mySettings] '
null =' >/dev/null 2>&1'

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("mySettings", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/mySettings/locale/"))

def _(txt):
	t = gettext.dgettext("mySettings", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block

config.plugins.mySettings = ConfigSubsection()
config.plugins.mySettings.freetv =		ConfigSelection(default= False, choices = [(False, _("No")),('freetv', _("Yes"))])
config.plugins.mySettings.hdplus =		ConfigSelection(default= False, choices = [(False, _("No")),('hdplus', _("Yes"))])
config.plugins.mySettings.skyde =		ConfigSelection(default= False, choices = [(False, _("No")),('skyde', _("Yes"))])
config.plugins.mySettings.skybliga = 	ConfigSelection(default= False, choices = [(False, _("No")),('skybliga', _("Yes"))])
config.plugins.mySettings.skysport =	ConfigSelection(default= False, choices = [(False, _("No")),('skysport', _("Yes"))])
config.plugins.mySettings.skyselect =	ConfigSelection(default= False, choices = [(False, _("No")),('skyselect', _("Yes"))])
config.plugins.mySettings.orf = 		ConfigSelection(default= False, choices = [(False, _("No")),('orf', _("Yes"))])
config.plugins.mySettings.childrens =	ConfigSelection(default= False, choices = [(False, _("No")),('childrens', _("Yes"))])
config.plugins.mySettings.shopping  =	ConfigSelection(default= False, choices = [(False, _("No")),('shopping', _("Yes"))])
config.plugins.mySettings.adult  =		ConfigSelection(default= False, choices = [(False, _("No")),('adult', _("Yes"))])
config.plugins.mySettings.srg =			ConfigSelection(default= False, choices = [(False, _("No")),('srg', _("Yes"))])
config.plugins.mySettings.erotik13e =	ConfigSelection(default= False, choices = [(False, _("No")),('erotik13e', _("Yes"))])
config.plugins.mySettings.dvbcfree =	ConfigSelection(default= False, choices = [(False, _("No")),('dvbcfree', _("Yes"))])
config.plugins.mySettings.dvbcsky =		ConfigSelection(default= False, choices = [(False, _("No")),('dvbcsky', _("Yes"))])
config.plugins.mySettings.dvbcskysport=	ConfigSelection(default= False, choices = [(False, _("No")),('dvbcskysport', _("Yes"))])
config.plugins.mySettings.dvbcpaytv =	ConfigSelection(default= False, choices = [(False, _("No")),('dvbcpaytv', _("Yes"))])

z1 = _("You can here download individual Channellist. Make your selection and press START (green)")
z2 = _("All exists Channellists will be irrevocably overwritten")
z3 = _("These Settings will not be lost after update. The must your here do self, if you want")

p00 =  z1 + '\n' + z2 + '\n' + z3 
p01 = _("Free TV HD")
p02 = _("HD +")
p03 = _("Sky Germany")
p04 = _("Sky Bundesliga")
p05 = _("Sky Sport")
p06 = _("Sky Select")
p07 = _("ORF")
p08 = _("Childrens")
p09 = _("Shopping")
p10 = _("Adult 19E")
p11 = _("Schweiz 13E")
p12 = _("Adult 13")
p13 = _("UMKBW Free TV")
p14 = _("UMKBW Sky")
p15 = _("UMKBW Sky Sport")
p16 = _("UMKBW Pay TV")


class mySettings(ConfigListScreen, Screen):
	skin ="""<screen name="mySettings-Setup" position="center,center" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
	<eLabel name="bg" position="center,center" zPosition="-2" size="900,640" backgroundColor="black" transparent="0" />
	<widget name="config" position="210,220" size="420,470" scrollbarMode="showOnDemand" transparent="1" backgroundColor="black" zPosition="1" />
	<widget name="HELPTEXT" position="651,220" size="420,470" zPosition="1" font="Regular; 20" halign="left"  backgroundColor="black" transparent="1" />
	<widget name="Title" position="211,72" size="860,50" zPosition="1" font="Regular; 32" halign="center"  backgroundColor="black" transparent="1" />
	<eLabel font="Regular; 20" zPosition="1" foregroundColor="black" halign="center" position="745,648" size="200,33" text="Cancel" transparent="1" backgroundColor="red" />
	<eLabel font="Regular; 20" zPosition="1" foregroundColor="white" halign="center" position="340,648" size="200,33" text="Start" transparent="1" backgroundColor="green" />
	<eLabel position="340,645" zPosition="0" size="200,33" backgroundColor="green" />
	<eLabel position="745,645" zPosition="0" size="200,33" backgroundColor="red" />
	<widget name="HELP" position="211,129" size="860,75" zPosition="1" font="Regular; 20" halign="left"  backgroundColor="black" transparent="1" />
	<eLabel text="mySettings 1.0 by Undertaker" position="517,45" size="250,21" zPosition="1" font="Regular; 15" halign="center" backgroundColor="black" transparent="1" foregroundColor="white" />
</screen>"""

	def __init__(self, session, args = None, picPath = None):
		self.config_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.Scale = AVSwitch().getFramebufferScale()
		self["HELPTEXT"] = Label()
		self["HELP"] = Label()
		self["HELP"].setText(p00)
		self["Title"] = Label()
		self["Title"].setText("mySettings " + _("Setup"))
		list =[]
		existlist = self.getexistlist()

		m02=""
		list.append(getConfigListEntry("01) " + _("Free TV HD"), config.plugins.mySettings.freetv, m02 + p01))
		list.append(getConfigListEntry("02) " + _("HD +"), config.plugins.mySettings.hdplus,m02 + m02 + p02))
		list.append(getConfigListEntry("03) " + _("Sky Germany"), config.plugins.mySettings.skyde, m02 + p03))
		list.append(getConfigListEntry("04) " + _("Sky Bundesliga"), config.plugins.mySettings.skybliga, m02 + p04))
		list.append(getConfigListEntry("05) " + _("Sky Sport"), config.plugins.mySettings.skysport,m02 +  p05))
		list.append(getConfigListEntry("06) " + _("Sky Select"), config.plugins.mySettings.skyselect,m02 +  p06))
		list.append(getConfigListEntry("07) " + _("ORF"), config.plugins.mySettings.orf, m02 + p07))
		list.append(getConfigListEntry("08) " + _("Childrens"), config.plugins.mySettings.childrens,m02 +  p08))
		list.append(getConfigListEntry("09) " + _("Shopping"), config.plugins.mySettings.shopping, m02 + p09))
		list.append(getConfigListEntry("10) " + _("Adult"), config.plugins.mySettings.adult, m02 + p10))
		list.append(getConfigListEntry("11) " + _("Schweiz 13E"), config.plugins.mySettings.srg, m02 + p11))
		list.append(getConfigListEntry("12) " + _("Adult 13E"), config.plugins.mySettings.erotik13e, m02 + p12))
		list.append(getConfigListEntry("13) " + _("UMKBW Free TV"), config.plugins.mySettings.dvbcfree,m02 +  p13))
		list.append(getConfigListEntry("14) " + _("UMKBW Sky"), config.plugins.mySettings.dvbcsky, m02 + p14))
		list.append(getConfigListEntry("15) " + _("UMKBW Sky Sport"), config.plugins.mySettings.dvbcskysport, m02 + p15))
		list.append(getConfigListEntry("16) " + _("UMKBW Pay TV"), config.plugins.mySettings.dvbcpaytv, m02 + p16))

		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.exit, "blue": self.exit, "green": self.save,"cancel": self.exit}, -1)
		#self.onLayoutFinish.append(self.machwas)

		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def selectionChanged(self):
		self["HELPTEXT"].setText(self["config"].getCurrent()[2])

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)

	def save(self):
		config.plugins.mySettings.save()        
		configfile.save()
		self.downloadmySettings()
		self.session.open(MessageBox, _("mySettings install finished\nhave fun"), MessageBox.TYPE_INFO, 10).setTitle(_("done"))
		self.close()

	def downloadmySettings(self):
		target = "/etc/enigma2/"
		list = []
		system('rm -f ' + target + '*.tv')
		system('rm -f ' + target + 'lamedb5')
		system('rm -f ' + target + 'lamedb')
		system('curl -s -o ' + target + 'lamedb '  + self.getdl() + 'lamedb')
		system('curl -s -o ' + target + 'lamedb5 ' + self.getdl() + 'lamedb5')

		if config.plugins.mySettings.freetv.value		!= False:list.append(config.plugins.mySettings.freetv.value)
		if config.plugins.mySettings.hdplus.value		!= False:list.append(config.plugins.mySettings.hdplus.value)
		if config.plugins.mySettings.skyde.value		!= False:list.append(config.plugins.mySettings.skyde.value)
		if config.plugins.mySettings.skybliga.value 	!= False:list.append(config.plugins.mySettings.skybliga.value)
		if config.plugins.mySettings.skysport.value 	!= False:list.append(config.plugins.mySettings.skysport.value)
		if config.plugins.mySettings.skyselect.value 	!= False:list.append(config.plugins.mySettings.skyselect.value)
		if config.plugins.mySettings.orf.value			!= False:list.append(config.plugins.mySettings.orf.value)
		if config.plugins.mySettings.srg.value			!= False:list.append(config.plugins.mySettings.srg.value)
		if config.plugins.mySettings.childrens.value 	!= False:list.append(config.plugins.mySettings.childrens.value)
		if config.plugins.mySettings.shopping.value 	!= False:list.append(config.plugins.mySettings.shopping.value)
		if config.plugins.mySettings.adult.value		!= False:list.append(config.plugins.mySettings.adult.value)
		if config.plugins.mySettings.erotik13e.value 	!= False:list.append(config.plugins.mySettings.erotik13e.value)
		if config.plugins.mySettings.dvbcfree.value 	!= False:list.append(config.plugins.mySettings.dvbcfree.value)
		if config.plugins.mySettings.dvbcsky.value 		!= False:list.append(config.plugins.mySettings.dvbcsky.value)
		if config.plugins.mySettings.dvbcskysport.value != False:list.append(config.plugins.mySettings.dvbcskysport.value)
		if config.plugins.mySettings.dvbcpaytv.value 	!= False:list.append(config.plugins.mySettings.dvbcpaytv.value)

		bouquetsfile = open(target + "bouquets.tv", "w")
		bouquetsfile.write("#NAME Bouquets (TV)" + "\n")

		for i in list:
			system('curl -s -o ' + target + 'userbouquet.' + i + '.tv ' + self.getdl() + 'userbouquet.'+ i + '.tv')
			if i == "freetv":
				system('mv ' + target + 'userbouquet.freetv.tv ' + target + 'userbouquet.favourites.tv')
				i = "favourites"
			bouquetsfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.' + i + '.tv" ORDER BY bouquet' + '\n')
		bouquetsfile.close()

		db = eDVBDB.getInstance()
		db.reloadServicelist()
		db.reloadBouquets()

	def getdl(self):
		return 'https://raw.githubusercontent.com/undertaker01/mySettings/master/downloads/'

	def getexistlist(self):
		target = "/etc/enigma2/"
		oldfile = open(target + "bouquets.tv", "r")
		existlist =[]
		for line in oldfile.readlines():
			if line.startswith('#SERVICE'):
				existlist.append(str(line.strip().split('"')[1].replace('userbouquet.','').replace('.tv','') ))
		oldfile.close()
		return existlist

	def makebackup(self):
		dd = (time.strftime("%Y-%m-%d-%H-%M-%S"))
		y = glob.glob(target + '*.tv')
		if len(y) >0:
			system('tar -czf ' + target + 'backup-mySettings-'+ dd +'.tar.gz ' + target + '*.tv')
			system('rm -f ' + target + '*.tv')

	def onlinecheck(self):
		try:
			response=urllib2.urlopen(base64.b64decode('aHR0cDovLzE5Mi4xODUuNDEuMjc='),timeout=2)
			return True
		except urllib2.URLError as err: pass
		return False

	def exit(self):
		system('rm -rf /tmp/data')
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
					pass
		self.close()

def main(session, **kwargs):
	session.open(mySettings,"/usr/lib/enigma2/python/Plugins/Extensions/mySettings/images/plugin.png")
def Plugins(**kwargs):
	return PluginDescriptor(name="mySettings v1.0", description=_("mySettings tool for Enigma2"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)
