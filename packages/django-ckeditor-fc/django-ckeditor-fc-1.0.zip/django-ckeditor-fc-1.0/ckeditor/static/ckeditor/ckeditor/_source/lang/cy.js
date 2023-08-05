﻿/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

/**
 * @fileOverview Defines the {@link CKEDITOR.lang} object, for the
 * Welsh language.
 */

/**#@+
   @type String
   @example
*/

/**
 * Constains the dictionary of language entries.
 * @namespace
 */
CKEDITOR.lang['cy'] =
{
	/**
	 * The language reading direction. Possible values are "rtl" for
	 * Right-To-Left languages (like Arabic) and "ltr" for Left-To-Right
	 * languages (like English).
	 * @default 'ltr'
	 */
	dir : 'ltr',

	/*
	 * Screenreader titles. Please note that screenreaders are not always capable
	 * of reading non-English words. So be careful while translating it.
	 */
	editorTitle : 'Golygydd testun cyfoethog, %1, gwasgwch ALT 0 am gymorth.',

	// ARIA descriptions.
	toolbars	: 'Bariau offer golygydd',
	editor		: 'Golygydd Testun Cyfoethog',

	// Toolbar buttons without dialogs.
	source			: 'Tarddle',
	newPage			: 'Tudalen newydd',
	save			: 'Cadw',
	preview			: 'Rhagolwg',
	cut				: 'Torri',
	copy			: 'Copïo',
	paste			: 'Gludo',
	print			: 'Argraffu',
	underline		: 'Tanlinellu',
	bold			: 'Bras',
	italic			: 'Italig',
	selectAll		: 'Dewis Popeth',
	removeFormat	: 'Tynnu Fformat',
	strike			: 'Llinell Trwyddo',
	subscript		: 'Is-sgript',
	superscript		: 'Uwchsgript',
	horizontalrule	: 'Mewnosod Llinell Lorweddol',
	pagebreak		: 'Mewnosod Toriad Tudalen i Argraffu',
	pagebreakAlt		: 'Toriad Tudalen',
	unlink			: 'Datgysylltu',
	undo			: 'Dadwneud',
	redo			: 'Ailadrodd',

	// Common messages and labels.
	common :
	{
		browseServer	: 'Pori\'r Gweinydd',
		url				: 'URL',
		protocol		: 'Protocol',
		upload			: 'Lanlwytho',
		uploadSubmit	: 'Anfon i\'r Gweinydd',
		image			: 'Delwedd',
		flash			: 'Flash',
		form			: 'Ffurflen',
		checkbox		: 'Blwch ticio',
		radio			: 'Botwm Radio',
		textField		: 'Maes Testun',
		textarea		: 'Ardal Testun',
		hiddenField		: 'Maes Cudd',
		button			: 'Botwm',
		select			: 'Maes Dewis',
		imageButton		: 'Botwm Delwedd',
		notSet			: '<heb osod>',
		id				: 'Id',
		name			: 'Name',
		langDir			: 'Cyfeiriad Iaith',
		langDirLtr		: 'Chwith i\'r Dde (LTR)',
		langDirRtl		: 'Dde i\'r Chwith (RTL)',
		langCode		: 'Cod Iaith',
		longDescr		: 'URL Disgrifiad Hir',
		cssClass		: 'Dosbarth Dalen Arddull',
		advisoryTitle	: 'Teitl Cynghorol',
		cssStyle		: 'Arddull',
		ok				: 'Iawn',
		cancel			: 'Diddymu',
		close			: 'Cau',
		preview			: 'Rhagolwg',
		generalTab		: 'Cyffredinol',
		advancedTab		: 'Uwch',
		validateNumberFailed : 'Nid yw\'r gwerth hwn yn rhif.',
		confirmNewPage	: 'Byddwch yn colli unrhyw newidiadau i\'r cynnwys sydd heb eu cadw. A ydych am barhau i lwytho tudalen newydd?',
		confirmCancel	: 'Mae rhai o\'r opsiynau wedi\'u newid. A ydych wir am gau\'r deialog?',
		options			: 'Opsiynau',
		target			: 'Targed',
		targetNew		: 'Ffenest Newydd (_blank)',
		targetTop		: 'Ffenest ar y Brig (_top)',
		targetSelf		: 'Yr un Ffenest (_self)',
		targetParent	: 'Ffenest y Rhiant (_parent)',
		langDirLTR		: 'Chwith i\'r Dde (LTR)',
		langDirRTL		: 'Dde i\'r Chwith (RTL)',
		styles			: 'Arddull',
		cssClasses		: 'Dosbarthiadau Ffeil Ddiwyg',
		width			: 'Lled',
		height			: 'Uchder',
		align			: 'Alinio',
		alignLeft		: 'Chwith',
		alignRight		: 'Dde',
		alignCenter		: 'Canol',
		alignTop		: 'Brig',
		alignMiddle		: 'Canol',
		alignBottom		: 'Gwaelod',
		invalidHeight	: 'Rhaid i\'r Uchder fod yn rhif.',
		invalidWidth	: 'Rhaid i\'r Lled fod yn rhif.',
		invalidCssLength	: 'Mae\'n rhaid i\'r gwerth ar gyfer maes "%1" fod yn rhif positif gyda neu heb uned fesuriad CSS dilys (px, %, in, cm, mm, em, ex, pt, neu pc).',
		invalidHtmlLength	: 'Mae\'n rhaid i\'r gwerth ar gyfer maes "%1" fod yn rhif positif gyda neu heb uned fesuriad HTML dilys (px neu %).',

		// Put the voice-only part of the label in the span.
		unavailable		: '%1<span class="cke_accessibility">, ddim ar gael</span>'
	},

	contextmenu :
	{
		options : 'Opsiynau Dewislen Cyd-destun'
	},

	// Special char dialog.
	specialChar		:
	{
		toolbar		: 'Mewnosod Nodau Arbennig',
		title		: 'Dewis Nod Arbennig',
		options : 'Opsiynau Nodau Arbennig'
	},

	// Link dialog.
	link :
	{
		toolbar		: 'Dolen',
		other 		: '<eraill>',
		menu		: 'Golygu Dolen',
		title		: 'Dolen',
		info		: 'Gwyb ar y Ddolen',
		target		: 'Targed',
		upload		: 'Lanlwytho',
		advanced	: 'Uwch',
		type		: 'Math y Ddolen',
		toUrl		: 'URL',
		toAnchor	: 'Dolen at angor yn y testun',
		toEmail		: 'E-bost',
		targetFrame		: '<ffrâm>',
		targetPopup		: '<ffenestr bop>',
		targetFrameName	: 'Enw Ffrâm y Targed',
		targetPopupName	: 'Enw Ffenestr Bop',
		popupFeatures	: 'Nodweddion Ffenestr Bop',
		popupResizable	: 'Ailfeintiol',
		popupStatusBar	: 'Bar Statws',
		popupLocationBar: 'Bar Safle',
		popupToolbar	: 'Bar Offer',
		popupMenuBar	: 'Dewislen',
		popupFullScreen	: 'Sgrin Llawn (IE)',
		popupScrollBars	: 'Barrau Sgrolio',
		popupDependent	: 'Dibynnol (Netscape)',
		popupLeft		: 'Safle Chwith',
		popupTop		: 'Safle Top',
		id				: 'Id',
		langDir			: 'Cyfeiriad Iaith',
		langDirLTR		: 'Chwith i\'r Dde (LTR)',
		langDirRTL		: 'Dde i\'r Chwith (RTL)',
		acccessKey		: 'Allwedd Mynediad',
		name			: 'Enw',
		langCode			: 'Cod Iaith',
		tabIndex			: 'Indecs Tab',
		advisoryTitle		: 'Teitl Cynghorol',
		advisoryContentType	: 'Math y Cynnwys Cynghorol',
		cssClasses		: 'Dosbarthiadau Dalen Arddull',
		charset			: 'Set nodau\'r Adnodd Cysylltiedig',
		styles			: 'Arddull',
		rel			: 'Perthynas',
		selectAnchor		: 'Dewiswch Angor',
		anchorName		: 'Gan Enw\'r Angor',
		anchorId			: 'Gan Id yr Elfen',
		emailAddress		: 'Cyfeiriad E-Bost',
		emailSubject		: 'Testun y Message Subject',
		emailBody		: 'Pwnc y Neges',
		noAnchors		: '(Dim angorau ar gael yn y ddogfen)',
		noUrl			: 'Teipiwch URL y ddolen',
		noEmail			: 'Teipiwch gyfeiriad yr e-bost'
	},

	// Anchor dialog
	anchor :
	{
		toolbar		: 'Angor',
		menu		: 'Golygwch yr Angor',
		title		: 'Priodweddau\'r Angor',
		name		: 'Enw\'r Angor',
		errorName	: 'Teipiwch enw\'r angor',
		remove		: 'Tynnwch yr Angor'
	},

	// List style dialog
	list:
	{
		numberedTitle		: 'Priodweddau Rhestr Rifol',
		bulletedTitle		: 'Priodweddau Rhestr Fwled',
		type				: 'Math',
		start				: 'Dechrau',
		validateStartNumber				:'Rhaid bod y rhif cychwynnol yn gyfanrif.',
		circle				: 'Cylch',
		disc				: 'Disg',
		square				: 'Sgwâr',
		none				: 'Dim',
		notset				: '<heb osod>',
		armenian			: 'Rhifau Armeneg',
		georgian			: 'Rhifau Sioraidd (an, ban, gan, ayyb.)',
		lowerRoman			: 'Rhufeinig Is (i, ii, iii, iv, v, ayyb.)',
		upperRoman			: 'Rhufeinig Uwch (I, II, III, IV, V, ayyb.)',
		lowerAlpha			: 'Alffa Is (a, b, c, d, e, ayyb.)',
		upperAlpha			: 'Alffa Uwch (A, B, C, D, E, ayyb.)',
		lowerGreek			: 'Groeg Is (alpha, beta, gamma, ayyb.)',
		decimal				: 'Degol (1, 2, 3, ayyb.)',
		decimalLeadingZero	: 'Degol â sero arweiniol (01, 02, 03, ayyb.)'
	},

	// Find And Replace Dialog
	findAndReplace :
	{
		title				: 'Chwilio ac Amnewid',
		find				: 'Chwilio',
		replace				: 'Amnewid',
		findWhat			: 'Chwilio\'r term:',
		replaceWith			: 'Amnewid gyda:',
		notFoundMsg			: 'Nid oedd y testun wedi\'i ddarganfod.',
		matchCase			: 'Cyfateb i\'r cas',
		matchWord			: 'Cyfateb gair cyfan',
		matchCyclic			: 'Cyfateb cylchol',
		replaceAll			: 'Amnewid pob un',
		replaceSuccessMsg	: 'Amnewidiwyd %1 achlysur.'
	},

	// Table Dialog
	table :
	{
		toolbar		: 'Tabl',
		title		: 'Nodweddion Tabl',
		menu		: 'Nodweddion Tabl',
		deleteTable	: 'Dileu Tabl',
		rows		: 'Rhesi',
		columns		: 'Colofnau',
		border		: 'Maint yr Ymyl',
		widthPx		: 'picsel',
		widthPc		: 'y cant',
		widthUnit	: 'uned lled',
		cellSpace	: 'Bylchu\'r gell',
		cellPad		: 'Padio\'r gell',
		caption		: 'Pennawd',
		summary		: 'Crynodeb',
		headers		: 'Penynnau',
		headersNone		: 'Dim',
		headersColumn	: 'Colofn gyntaf',
		headersRow		: 'Rhes gyntaf',
		headersBoth		: 'Y Ddau',
		invalidRows		: 'Mae\'n rhaid cael o leiaf un rhes.',
		invalidCols		: 'Mae\'n rhaid cael o leiaf un golofn.',
		invalidBorder	: 'Mae\'n rhaid i faint yr ymyl fod yn rhif.',
		invalidWidth	: 'Mae\'n rhaid i led y tabl fod yn rhif.',
		invalidHeight	: 'Mae\'n rhaid i uchder y tabl fod yn rhif.',
		invalidCellSpacing	: 'Mae\'n rhaid i fylchiad y gell fod yn rhif positif.',
		invalidCellPadding	: 'Mae\'n rhaid i badiad y gell fod yn rhif positif.',

		cell :
		{
			menu			: 'Cell',
			insertBefore	: 'Mewnosod Cell Cyn',
			insertAfter		: 'Mewnosod Cell Ar Ôl',
			deleteCell		: 'Dileu Celloedd',
			merge			: 'Cyfuno Celloedd',
			mergeRight		: 'Cyfuno i\'r Dde',
			mergeDown		: 'Cyfuno i Lawr',
			splitHorizontal	: 'Hollti\'r Gell yn Lorweddol',
			splitVertical	: 'Hollti\'r Gell yn Fertigol',
			title			: 'Priodweddau\'r Gell',
			cellType		: 'Math y Gell',
			rowSpan			: 'Rhychwant Rhesi',
			colSpan			: 'Rhychwant Colofnau',
			wordWrap		: 'Lapio Geiriau',
			hAlign			: 'Aliniad Llorweddol',
			vAlign			: 'Aliniad Fertigol',
			alignBaseline	: 'Baslinell',
			bgColor			: 'Lliw Cefndir',
			borderColor		: 'Lliw Ymyl',
			data			: 'Data',
			header			: 'Pennyn',
			yes				: 'Ie',
			no				: 'Na',
			invalidWidth	: 'Mae\'n rhaid i led y gell fod yn rhif.',
			invalidHeight	: 'Mae\'n rhaid i uchder y gell fod yn rhif.',
			invalidRowSpan	: 'Mae\'n rhaid i rychwant y rhesi fod yn gyfanrif.',
			invalidColSpan	: 'Mae\'n rhaid i rychwant y colofnau fod yn gyfanrif.',
			chooseColor		: 'Choose'
		},

		row :
		{
			menu			: 'Rhes',
			insertBefore	: 'Mewnosod Rhes Cyn',
			insertAfter		: 'Mewnosod Rhes Ar Ôl',
			deleteRow		: 'Dileu Rhesi'
		},

		column :
		{
			menu			: 'Colofn',
			insertBefore	: 'Mewnosod Colofn Cyn',
			insertAfter		: 'Mewnosod Colofn Ar Ôl',
			deleteColumn	: 'Dileu Colofnau'
		}
	},

	// Button Dialog.
	button :
	{
		title		: 'Priodweddau Botymau',
		text		: 'Testun (Gwerth)',
		type		: 'Math',
		typeBtn		: 'Botwm',
		typeSbm		: 'Gyrru',
		typeRst		: 'Ailosod'
	},

	// Checkbox and Radio Button Dialogs.
	checkboxAndRadio :
	{
		checkboxTitle : 'Priodweddau Blwch Ticio',
		radioTitle	: 'Priodweddau Botwm Radio',
		value		: 'Gwerth',
		selected	: 'Dewiswyd'
	},

	// Form Dialog.
	form :
	{
		title		: 'Priodweddau Ffurflen',
		menu		: 'Priodweddau Ffurflen',
		action		: 'Gweithred',
		method		: 'Dull',
		encoding	: 'Amgodio'
	},

	// Select Field Dialog.
	select :
	{
		title		: 'Priodweddau Maes Dewis',
		selectInfo	: 'Gwyb Dewis',
		opAvail		: 'Opsiynau ar Gael',
		value		: 'Gwerth',
		size		: 'Maint',
		lines		: 'llinellau',
		chkMulti	: 'Caniatàu aml-ddewisiadau',
		opText		: 'Testun',
		opValue		: 'Gwerth',
		btnAdd		: 'Ychwanegu',
		btnModify	: 'Newid',
		btnUp		: 'Lan',
		btnDown		: 'Lawr',
		btnSetValue : 'Gosod fel gwerth a ddewiswyd',
		btnDelete	: 'Dileu'
	},

	// Textarea Dialog.
	textarea :
	{
		title		: 'Priodweddau Ardal Testun',
		cols		: 'Colofnau',
		rows		: 'Rhesi'
	},

	// Text Field Dialog.
	textfield :
	{
		title		: 'Priodweddau Maes Testun',
		name		: 'Enw',
		value		: 'Gwerth',
		charWidth	: 'Lled Nod',
		maxChars	: 'Uchafswm y Nodau',
		type		: 'Math',
		typeText	: 'Testun',
		typePass	: 'Cyfrinair'
	},

	// Hidden Field Dialog.
	hidden :
	{
		title	: 'Priodweddau Maes Cudd',
		name	: 'Enw',
		value	: 'Gwerth'
	},

	// Image Dialog.
	image :
	{
		title		: 'Priodweddau Delwedd',
		titleButton	: 'Priodweddau Botwm Delwedd',
		menu		: 'Priodweddau Delwedd',
		infoTab		: 'Gwyb Delwedd',
		btnUpload	: 'Anfon i\'r Gweinydd',
		upload		: 'lanlwytho',
		alt			: 'Testun Amgen',
		lockRatio	: 'Cloi Cymhareb',
		resetSize	: 'Ailosod Maint',
		border		: 'Ymyl',
		hSpace		: 'BwlchLl',
		vSpace		: 'BwlchF',
		alertUrl	: 'Rhowch URL y ddelwedd',
		linkTab		: 'Dolen',
		button2Img	: 'Ydych am drawsffurfio\'r botwm ddelwedd hwn ar ddelwedd syml?',
		img2Button	: 'Ydych am drawsffurfio\'r ddelwedd hon ar fotwm delwedd?',
		urlMissing	: 'URL tarddle\'r ddelwedd ar goll.',
		validateBorder	: 'Rhaid i\'r ymyl fod yn gyfanrif.',
		validateHSpace	: 'Rhaid i\'r HSpace fod yn gyfanrif.',
		validateVSpace	: 'Rhaid i\'r VSpace fod yn gyfanrif.'
	},

	// Flash Dialog
	flash :
	{
		properties		: 'Priodweddau Flash',
		propertiesTab	: 'Priodweddau',
		title			: 'Priodweddau Flash',
		chkPlay			: 'AwtoChwarae',
		chkLoop			: 'Lwpio',
		chkMenu			: 'Galluogi Dewislen Flash',
		chkFull			: 'Caniatàu Sgrin Llawn',
 		scale			: 'Graddfa',
		scaleAll		: 'Dangos pob',
		scaleNoBorder	: 'Dim Ymyl',
		scaleFit		: 'Ffit Union',
		access			: 'Mynediad Sgript',
		accessAlways	: 'Pob amser',
		accessSameDomain: 'R\'un parth',
		accessNever		: 'Byth',
		alignAbsBottom	: 'Gwaelod Abs',
		alignAbsMiddle	: 'Canol Abs',
		alignBaseline	: 'Baslinell',
		alignTextTop	: 'Testun Top',
		quality			: 'Ansawdd',
		qualityBest		: 'Gorau',
		qualityHigh		: 'Uchel',
		qualityAutoHigh	: 'Uchel Awto',
		qualityMedium	: 'Canolig',
		qualityAutoLow	: 'Isel Awto',
		qualityLow		: 'Isel',
		windowModeWindow: 'Ffenestr',
		windowModeOpaque: 'Afloyw',
		windowModeTransparent : 'Tryloyw',
		windowMode		: 'Modd ffenestr',
		flashvars		: 'Newidynnau ar gyfer Flash',
		bgcolor			: 'Lliw cefndir',
		hSpace			: 'BwlchLl',
		vSpace			: 'BwlchF',
		validateSrc		: 'Ni all yr URL fod yn wag.',
		validateHSpace	: 'Rhaid i\'r BwlchLl fod yn rhif.',
		validateVSpace	: 'Rhaid i\'r BwlchF fod yn rhif.'
	},

	// Speller Pages Dialog
	spellCheck :
	{
		toolbar			: 'Gwirio Sillafu',
		title			: 'Gwirio Sillafu',
		notAvailable	: 'Nid yw\'r gwasanaeth hwn ar gael yn bresennol.',
		errorLoading	: 'Error loading application service host: %s.',
		notInDic		: 'Nid i\'w gael yn y geiriadur',
		changeTo		: 'Newid i',
		btnIgnore		: 'Anwybyddu Un',
		btnIgnoreAll	: 'Anwybyddu Pob',
		btnReplace		: 'Amnewid Un',
		btnReplaceAll	: 'Amnewid Pob',
		btnUndo			: 'Dadwneud',
		noSuggestions	: '- Dim awgrymiadau -',
		progress		: 'Gwirio sillafu yn ar y gweill...',
		noMispell		: 'Gwirio sillafu wedi gorffen: Dim camsillaf.',
		noChanges		: 'Gwirio sillafu wedi gorffen: Dim newidiadau',
		oneChange		: 'Gwirio sillafu wedi gorffen: Newidiwyd 1 gair',
		manyChanges		: 'Gwirio sillafu wedi gorffen: Newidiwyd %1 gair',
		ieSpellDownload	: 'Gwirydd sillafu heb ei arsefydlu. A ydych am ei lawrlwytho nawr?'
	},

	smiley :
	{
		toolbar	: 'Gwenoglun',
		title	: 'Mewnosod Gwenoglun',
		options : 'Opsiynau Gwenogluniau'
	},

	elementsPath :
	{
		eleLabel : 'Llwybr elfennau',
		eleTitle : 'Elfen %1'
	},

	numberedlist	: 'Mewnosod/Tynnu Rhestr Rhifol',
	bulletedlist	: 'Mewnosod/Tynnu Rhestr Bwled',
	indent			: 'Cynyddu\'r Mewnoliad',
	outdent			: 'Lleihau\'r Mewnoliad',

	justify :
	{
		left	: 'Alinio i\'r Chwith',
		center	: 'Alinio i\'r Canol',
		right	: 'Alinio i\'r Dde',
		block	: 'Aliniad Bloc'
	},

	blockquote : 'Dyfyniad bloc',

	clipboard :
	{
		title		: 'Gludo',
		cutError	: 'Nid yw gosodiadau diogelwch eich porwr yn caniatàu\'r golygydd i gynnal \'gweithredoedd torri\' yn awtomatig. Defnyddiwch y bysellfwrdd (Ctrl/Cmd+X).',
		copyError	: 'Nid yw gosodiadau diogelwch eich porwr yn caniatàu\'r golygydd i gynnal \'gweithredoedd copïo\' yn awtomatig. Defnyddiwch y bysellfwrdd (Ctrl/Cmd+C).',
		pasteMsg	: 'Gludwch i mewn i\'r blwch canlynol gan ddefnyddio\'r bysellfwrdd (<strong>Ctrl/Cmd+V</strong>) a phwyso <strong>Iawn</strong>.',
		securityMsg	: 'Oherwydd gosodiadau diogelwch eich porwr, nid yw\'r porwr yn gallu ennill mynediad i\'r data ar y clipfwrdd yn uniongyrchol. Mae angen i chi ei ludo eto i\'r ffenestr hon.',
		pasteArea	: 'Ardal Gludo'
	},

	pastefromword :
	{
		confirmCleanup	: 'Mae\'r testun rydych chi am ludo wedi\'i gopïo o Word. Ydych chi am ei lanhau cyn ei ludo?',
		toolbar			: 'Gludo o Word',
		title			: 'Gludo o Word',
		error			: 'Doedd dim modd glanhau y data a ludwyd oherwydd gwall mewnol'
	},

	pasteText :
	{
		button	: 'Gludo fel testun plaen',
		title	: 'Gludo fel Testun Plaen'
	},

	templates :
	{
		button			: 'Templedi',
		title			: 'Templedi Cynnwys',
		options : 'Opsiynau Templedi',
		insertOption	: 'Amnewid y cynnwys go iawn',
		selectPromptMsg	: 'Dewiswch dempled i\'w agor yn y golygydd',
		emptyListMsg	: '(Dim templedi wedi\'u diffinio)'
	},

	showBlocks : 'Dangos Blociau',

	stylesCombo :
	{
		label		: 'Arddulliau',
		panelTitle	: 'Arddulliau Fformatio',
		panelTitle1	: 'Arddulliau Bloc',
		panelTitle2	: 'Arddulliau Mewnol',
		panelTitle3	: 'Arddulliau Gwrthrych'
	},

	format :
	{
		label		: 'Fformat',
		panelTitle	: 'Fformat Paragraff',

		tag_p		: 'Normal',
		tag_pre		: 'Wedi\'i Fformatio',
		tag_address	: 'Cyfeiriad',
		tag_h1		: 'Pennawd 1',
		tag_h2		: 'Pennawd 2',
		tag_h3		: 'Pennawd 3',
		tag_h4		: 'Pennawd 4',
		tag_h5		: 'Pennawd 5',
		tag_h6		: 'Pennawd 6',
		tag_div		: 'Normal (DIV)'
	},

	div :
	{
		title				: 'Creu Cynhwysydd Div',
		toolbar				: 'Creu Cynhwysydd Div',
		cssClassInputLabel	: 'Dosbarthiadau Ffeil Ddiwyg',
		styleSelectLabel	: 'Arddull',
		IdInputLabel		: 'Id',
		languageCodeInputLabel	: ' Cod Iaith',
		inlineStyleInputLabel	: 'Arddull Mewn Llinell',
		advisoryTitleInputLabel	: 'Teitl Cynghorol',
		langDirLabel		: 'Cyfeiriad yr Iaith',
		langDirLTRLabel		: 'Chwith i\'r Dde (LTR)',
		langDirRTLLabel		: 'Dde i\'r Chwith (RTL)',
		edit				: 'Golygu Div',
		remove				: 'Tynnu Div'
  	},

	iframe :
	{
		title		: 'Priodweddau IFrame',
		toolbar		: 'IFrame',
		noUrl		: 'Rhowch fath URL yr iframe',
		scrolling	: 'Galluogi bariau sgrolio',
		border		: 'Dangos ymyl y ffrâm'
	},

	font :
	{
		label		: 'Ffont',
		voiceLabel	: 'Ffont',
		panelTitle	: 'Enw\'r Ffont'
	},

	fontSize :
	{
		label		: 'Maint',
		voiceLabel	: 'Maint y Ffont',
		panelTitle	: 'Maint y Ffont'
	},

	colorButton :
	{
		textColorTitle	: 'Lliw Testun',
		bgColorTitle	: 'Lliw Cefndir',
		panelTitle		: 'Lliwiau',
		auto			: 'Awtomatig',
		more			: 'Mwy o Liwiau...'
	},

	colors :
	{
		'000' : 'Du',
		'800000' : 'Marwn',
		'8B4513' : 'Brown Cyfrwy',
		'2F4F4F' : 'Llechen Tywyll',
		'008080' : 'Corhwyad',
		'000080' : 'Nefi',
		'4B0082' : 'Indigo',
		'696969' : 'Llwyd Pwl',
		'B22222' : 'Bric Tân',
		'A52A2A' : 'Brown',
		'DAA520' : 'Rhoden Aur',
		'006400' : 'Gwyrdd Tywyll',
		'40E0D0' : 'Gwyrddlas',
		'0000CD' : 'Glas Canolig',
		'800080' : 'Porffor',
		'808080' : 'Llwyd',
		'F00' : 'Coch',
		'FF8C00' : 'Oren Tywyll',
		'FFD700' : 'Aur',
		'008000' : 'Gwyrdd',
		'0FF' : 'Cyan',
		'00F' : 'Glas',
		'EE82EE' : 'Fioled',
		'A9A9A9' : 'Llwyd Tywyll',
		'FFA07A' : 'Samwn Golau',
		'FFA500' : 'Oren',
		'FFFF00' : 'Melyn',
		'00FF00' : 'Leim',
		'AFEEEE' : 'Gwyrddlas Golau',
		'ADD8E6' : 'Glas Golau',
		'DDA0DD' : 'Eirinen',
		'D3D3D3' : 'Llwyd Golau',
		'FFF0F5' : 'Gwrid Lafant',
		'FAEBD7' : 'Gwyn Hynafol',
		'FFFFE0' : 'Melyn Golau',
		'F0FFF0' : 'Melwn Gwyrdd Golau',
		'F0FFFF' : 'Aswr',
		'F0F8FF' : 'Glas Alys',
		'E6E6FA' : 'Lafant',
		'FFF' : 'Gwyn'
	},

	scayt :
	{
		title			: 'Gwirio\'r Sillafu Wrth Deipio',
		opera_title		: 'Heb ei gynnal gan Opera',
		enable			: 'Galluogi SCAYT',
		disable			: 'Analluogi SCAYT',
		about			: 'Ynghylch SCAYT',
		toggle			: 'Togl SCAYT',
		options			: 'Opsiynau',
		langs			: 'Ieithoedd',
		moreSuggestions	: 'Awgrymiadau pellach',
		ignore			: 'Anwybyddu',
		ignoreAll		: 'Anwybyddu pob',
		addWord			: 'Ychwanegu Gair',
		emptyDic		: 'Ni ddylai enw\'r geiriadur fod yn wag.',

		optionsTab		: 'Opsiynau',
		allCaps			: 'Anwybyddu Geiriau Nodau Uwch i Gyd',
		ignoreDomainNames : 'Anwybyddu Enwau Parth',
		mixedCase		: 'Anwybyddu Geiriau â Chymysgedd Nodau Uwch ac Is',
		mixedWithDigits	: 'Anwybyddu Geiriau â Rhifau',

		languagesTab	: 'Ieithoedd',

		dictionariesTab	: 'Geiriaduron',
		dic_field_name	: 'Enw\'r geiriadur',
		dic_create		: 'Creu',
		dic_restore		: 'Adfer',
		dic_delete		: 'Dileu',
		dic_rename		: 'Ailenwi',
		dic_info		: 'Ar y cychwyn, caiff y Geiriadur ei storio mewn Cwci. Er, mae terfyn ar faint cwcis. Pan fydd Gweiriadur Defnyddiwr yn tyfu tu hwnt i gyfyngiadau maint Cwci, caiff y geiriadur ei storio ar ein gweinydd ni. er mwyn storio eich geiriadur poersonol chi ar ein gweinydd, bydd angen i chi osod enw ar gyfer y geiriadur. Os oes geiriadur \'da chi ar ein gweinydd yn barod, teipiwch ei enw a chliciwch y botwm Adfer.',

		aboutTab		: 'Ynghylch'
	},

	about :
	{
		title		: 'Ynghylch CKEditor',
		dlgTitle	: 'Ynghylch CKEditor',
		help	: 'Gwirio $1 am gymorth.',
		userGuide : 'Canllawiau Defnyddiwr CKEditor',
		moreInfo	: 'Am wybodaeth ynghylch trwyddedau, ewch i\'n gwefan:',
		copy		: 'Hawlfraint &copy; $1. Cedwir pob hawl.'
	},

	maximize : 'Mwyhau',
	minimize : 'Lleihau',

	fakeobjects :
	{
		anchor		: 'Angor',
		flash		: 'Animeiddiant Flash',
		iframe		: 'IFrame',
		hiddenfield	: 'Maes Cudd',
		unknown		: 'Gwrthrych Anhysbys'
	},

	resize : 'Llusgo i ailfeintio',

	colordialog :
	{
		title		: 'Dewis lliw',
		options	:	'Opsiynau Lliw',
		highlight	: 'Uwcholeuo',
		selected	: 'Dewiswyd',
		clear		: 'Clirio'
	},

	toolbarCollapse	: 'Cyfangu\'r Bar Offer',
	toolbarExpand	: 'Ehangu\'r Bar Offer',

	toolbarGroups :
	{
		document : 'Dogfen',
		clipboard : 'Clipfwrdd/Dadwneud',
		editing : 'Golygu',
		forms : 'Ffurflenni',
		basicstyles : 'Arddulliau Sylfaenol',
		paragraph : 'Paragraff',
		links : 'Dolenni',
		insert : 'Mewnosod',
		styles : 'Arddulliau',
		colors : 'Lliwiau',
		tools : 'Offer'
	},

	bidi :
	{
		ltr : 'Cyfeiriad testun o\'r chwith i\'r dde',
		rtl : 'Cyfeiriad testun o\'r dde i\'r chwith'
	},

	docprops :
	{
		label : 'Priodweddau Dogfen',
		title : 'Priodweddau Dogfen',
		design : 'Cynllunio',
		meta : 'Tagiau Meta',
		chooseColor : 'Dewis',
		other : 'Arall...',
		docTitle :	'Teitl y Dudalen',
		charset : 	'Amgodio Set Nodau',
		charsetOther : 'Amgodio Set Nodau Arall',
		charsetASCII : 'ASCII',
		charsetCE : 'Ewropeaidd Canol',
		charsetCT : 'Tsieinëeg Traddodiadol (Big5)',
		charsetCR : 'Syrilig',
		charsetGR : 'Groeg',
		charsetJP : 'Siapanëeg',
		charsetKR : 'Corëeg',
		charsetTR : 'Tyrceg',
		charsetUN : 'Unicode (UTF-8)',
		charsetWE : 'Ewropeaidd Gorllewinol',
		docType : 'Pennawd Math y Ddogfen',
		docTypeOther : 'Pennawd Math y Ddogfen Arall',
		xhtmlDec : 'Cynnwys Datganiadau XHTML',
		bgColor : 'Lliw Cefndir',
		bgImage : 'URL Delwedd Cefndir',
		bgFixed : 'Cefndir Sefydlog (Ddim yn Sgrolio)',
		txtColor : 'Lliw y Testun',
		margin : 'Ffin y Dudalen',
		marginTop : 'Brig',
		marginLeft : 'Chwith',
		marginRight : 'Dde',
		marginBottom : 'Gwaelod',
		metaKeywords : 'Allweddeiriau Indecsio Dogfen (gwahanu gyda choma)',
		metaDescription : 'Disgrifiad y Ddogfen',
		metaAuthor : 'Awdur',
		metaCopyright : 'Hawlfraint',
		previewHtml : '<p>Dyma ychydig o <strong>destun sampl</strong>. Rydych chi\'n defnyddio <a href="javascript:void(0)">CKEditor</a>.</p>'
	}
};
