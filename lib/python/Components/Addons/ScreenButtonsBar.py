from Components.Addons.GUIAddon import GUIAddon

from enigma import eListbox, eListboxPythonMultiContent, BT_ALIGN_CENTER, RT_VALIGN_CENTER, RT_HALIGN_LEFT, RT_HALIGN_CENTER, RT_BLEND, BT_SCALE, eSize, getDesktop, gFont

from skin import parseScale, parseColor, parseFont, applySkinFactor

from Components.MultiContent import MultiContentEntryPixmapAlphaBlend, MultiContentEntryText
from Components.Label import Label

from Tools.Directories import resolveFilename, SCOPE_GUISKIN
from Tools.LoadPixmap import LoadPixmap


class ScreenButtonsBar(GUIAddon):
	def __init__(self):
		GUIAddon.__init__(self)
		self.foreColor = None
		self.font = gFont("Regular", 18)
		self.l = eListboxPythonMultiContent()  # noqa: E741
		self.l.setBuildFunc(self.buildEntry)
		self.l.setItemHeight(35)
		self.l.setItemWidth(35)
		self.spacingButtons = applySkinFactor(40)
		self.spacingPixmapText = applySkinFactor(10)
		self.layoutStyle = "fixed"
		self.colorIndicatorStyle = "pixmap"
		self.orientations = {"orHorizontal": eListbox.orHorizontal, "orVertical": eListbox.orVertical}
		self.orientation = eListbox.orHorizontal
		self.actionButtonsPosition = "farRight" # can be left, right, farRight
		self.renderType = "ImageTextRight"  # Currently supported are ImageTextRight, ImageTextOver and ColorTextOver
		self.alignment = "left"
		self.cornerRadius = 0
		self.pixmaps = {}
		self.colors = {}
		self.textRenderer = Label("")
		self.colorButtonSources = {}
		self.actionButtonSources = {}
		self.spacing = applySkinFactor(10)
		self.spacingBetweenActionAndColorGroups = applySkinFactor(60)

	def onContainerShown(self):
		for x, val in self.sources.items():
			if x in ("key_red","key_green","key_yellow","key_blue"):
				self.colorButtonSources[x] = val
			else:
				self.actionButtonSources[x] = val
			if self.constructButtonSequence not in val.onChanged:
				val.onChanged.append(self.constructButtonSequence)
		self.textRenderer.GUIcreate(self.relatedScreen.instance)
		self.l.setItemHeight(self.instance.size().height())
		self.l.setItemWidth(self.instance.size().width())
		self.constructButtonSequence()

	GUI_WIDGET = eListbox

	def updateAddon(self, sequenceColor, sequenceAction):
		l_list = []
		l_list.append((sequenceColor, sequenceAction))
		self.l.setList(l_list)

	def buildEntry(self, sequence, sequenceAction):
		res = [None]
		if len(sequence) == 0 and len(sequenceAction) == 0:
			return res
		width = self.instance.size().width()
		height = self.instance.size().height()
		xPosAction = 0
		last_pixd_width = 0
		if self.actionButtonsPosition != "right":
			xPosAction = width if self.actionButtonsPosition == "farRight" else 0
			if self.actionButtonsPosition == "farRight":
				sequenceAction.reverse()
			for x in sequenceAction:
				if x in self.pixmaps:
					pic = LoadPixmap(resolveFilename(SCOPE_GUISKIN, self.pixmaps[x]))
					if pic:
						pixd_size = pic.size()
						pixd_width = pixd_size.width()
						pixd_height = pixd_size.height()
						pic_x_pos = (xPosAction - pixd_width) if self.actionButtonsPosition == "farRight" else xPosAction
						res.append(MultiContentEntryPixmapAlphaBlend(
							pos=(pic_x_pos, (height - pixd_height) // 2),
							size=(pixd_width, pixd_height),
							png=pic,
							backcolor=None, backcolor_sel=None, flags=BT_ALIGN_CENTER))
						if self.actionButtonsPosition == "farRight":
							xPosAction -= pixd_width + self.spacing
						else:
							xPosAction += pixd_width + self.spacing
					last_pixd_width = pixd_width
			if self.actionButtonsPosition == "farRight":
				xPosAction += last_pixd_width + self.spacing

		xPos = (xPosAction + self.spacingBetweenActionAndColorGroups) if self.actionButtonsPosition != "farRight" else 0
		yPos = 0
		width_color_reserved = (width - xPosAction - self.spacingBetweenActionAndColorGroups) if self.actionButtonsPosition != "farRight" else xPosAction - self.spacingBetweenActionAndColorGroups
		minSectorWidth = width_color_reserved // 4

		pic = None
		pixd_width = 0

		for x, val in sequence.items():
			textColor = self.foreColor
			buttonBgColor = self.foreColor

			if x in self.colors:
				if self.renderType == "ImageTextRight":
					textColor = parseColor(self.colors[x]).argb()
				else:
					buttonBgColor = parseColor(self.colors[x]).argb()

			if self.renderType != "ImageTextOver" and x in self.pixmaps:
				pic = LoadPixmap(resolveFilename(SCOPE_GUISKIN, self.pixmaps[x]))
				if pic:
					pixd_size = pic.size()
					pixd_width = pixd_size.width()
					pic_x_pos = (xPos - pixd_width) if self.alignment == "right" else xPos
					res.append(MultiContentEntryPixmapAlphaBlend(
						pos=(pic_x_pos, yPos),
						size=(pixd_width, height),
						png=pic,
						backcolor=None, backcolor_sel=None, flags=BT_ALIGN_CENTER))
					if self.alignment == "right":
						xPos -= pixd_width + self.spacingPixmapText
					else:
						xPos += pixd_width + self.spacingPixmapText
			if hasattr(val, "text"):
				buttonText = val.text
			else:
				buttonText = ""

			if buttonText:
				textWidth = self._calcTextWidth(buttonText, font=self.font, size=eSize(self.getDesktopWith() // 3, 0))
			else:
				textWidth = 0
			if self.layoutStyle != "fluid":
				if textWidth < (minSectorWidth - self.spacingButtons - (self.spacingPixmapText if pic else 0) - pixd_width):
					textWidth = minSectorWidth - self.spacingButtons - (self.spacingPixmapText if pic else 0) - pixd_width
			if buttonText:
				textFlags = RT_HALIGN_LEFT | RT_VALIGN_CENTER
				textPaddings = 0
				backColor = None
				if self.renderType in ["ColorTextOver", "ImageTextOver"]:
					textFlags = RT_HALIGN_CENTER | RT_VALIGN_CENTER
					textPaddings = self.spacingPixmapText
					backColor = buttonBgColor

				if self.renderType == "ImageTextOver":
					textFlags = textFlags | RT_BLEND
					if x in self.pixmaps:
						pic = LoadPixmap(resolveFilename(SCOPE_GUISKIN, self.pixmaps[x]))
						if pic:
							res.append(MultiContentEntryPixmapAlphaBlend(
								pos=(xPos, yPos),
								size=(textWidth + textPaddings * 2, height),
								png=pic,
								backcolor=0x000000, backcolor_sel=None, flags=BT_SCALE, corner_radius=self.cornerRadius))
						res.append(MultiContentEntryText(
							pos=(xPos + textPaddings, yPos), size=(textWidth, height - 2),
							font=0, flags=textFlags,
							text=buttonText, color=textColor, color_sel=textColor))
				else:
					res.append(MultiContentEntryText(
						pos=(xPos, yPos), size=(textWidth + textPaddings * 2, height - 2),
						font=0, flags=textFlags,
						text=buttonText, color=textColor, color_sel=textColor, backcolor=backColor, corner_radius=self.cornerRadius))

				xPos += textWidth + textPaddings * 2 + self.spacingButtons
			if xPos - ((xPosAction + self.spacingBetweenActionAndColorGroups) if self.actionButtonsPosition != "farRight" else 0) > width_color_reserved and self.layoutStyle != "fluid":
				print("[ScreenButtonsBar] SWITCH TO FLUID: xPos = %d > width = %d" % (xPos, width_color_reserved))
				self.layoutStyle = "fluid"
				return self.buildEntry(sequence, sequenceAction)

		return res

	def postWidgetCreate(self, instance):
		instance.setSelectionEnable(False)
		instance.setContent(self.l)
		instance.allowNativeKeys(False)

	def constructButtonSequence(self):
		sequenceColor = {}
		sequenceAction = []
		for x, val in self.colorButtonSources.items():
			if hasattr(val, "text") and val.text:
				sequenceColor[x] = val

		for x, val in self.actionButtonSources.items():
			if hasattr(val, "boolean") and val.boolean and x not in sequenceAction:
				sequenceAction.append(x)

		self.updateAddon(sequenceColor, sequenceAction)

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value) in self.skinAttributes[:]:
			if attrib == "actionButtonsPos":
				self.actionButtonsPosition = value
			elif attrib == "pixmaps":
				self.pixmaps = dict(item.split(':') for item in value.split(','))
			elif attrib == "spacingColor":
				self.spacingButtons = parseScale(value)
			elif attrib == "spacingAction":
				self.spacing = parseScale(value)
			elif attrib == "spacingPixmapText":
				self.spacingPixmapText = parseScale(value)
			elif attrib == "spacingActionColorGroups":
				self.spacingBetweenActionAndColorGroups = parseScale(value)
			elif attrib == "layoutStyle":
				self.layoutStyle = value
			elif attrib == "alignment":
				self.alignment = value
			elif attrib == "orientation":
				self.orientation = self.orientations.get(value, self.orientations["orHorizontal"])
				if self.orientation == eListbox.orHorizontal:
					self.instance.setOrientation(eListbox.orVertical)
					self.l.setOrientation(eListbox.orVertical)
				else:
					self.instance.setOrientation(eListbox.orHorizontal)
					self.l.setOrientation(eListbox.orHorizontal)
			elif attrib == "font":
				self.font = parseFont(value, parent.scale)
			elif attrib == "foregroundColor":
				self.foreColor = parseColor(value).argb()
			elif attrib == "textColors":
				self.colors = dict(item.split(':') for item in value.split(','))
			elif attrib == "buttonCornerRadius":
				self.cornerRadius = parseScale(value)
			elif attrib == "renderType":
				self.renderType = value
			else:
				attribs.append((attrib, value))
		self.skinAttributes = attribs
		self.l.setFont(0, self.font)
		return GUIAddon.applySkin(self, desktop, parent)

	def _calcTextWidth(self, text, font=None, size=None):
		if size:
			self.textRenderer.instance.resize(size)
		if font:
			self.textRenderer.instance.setFont(font)
		self.textRenderer.text = text
		return self.textRenderer.instance.calculateSize().width()

	def getDesktopWith(self):
		return getDesktop(0).size().width()
