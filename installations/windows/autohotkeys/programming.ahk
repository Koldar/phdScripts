#CommentFlag //

// **************************************************************
// ************************ GENERAL *****************************
// **************************************************************

//avoid display update dialog when updating the script
#SingleInstance Force
// force the installation of keyboard hook (mandatory for the Altgr+ì shortcut
#InstallKeybdHook
//Keeps a script permanently running (that is, until the user closes it or ExitApp is encountered).
#Persistent

// **************************************************************
// ************************ SOUND *******************************
// **************************************************************

// increase volume
// Control + Arrow Up
^Up::
SoundSet, +3
return

// decrease volume
// Control + Arrow Down
^Down::
SoundSet, -3
return

// **************************************************************
// ******************** SPECIAL SYMBOLS *************************
// **************************************************************

// AltGr + ' needs to generate tilde
<^>!'::
SendInput, ``
return

// AltGr + ì ((U+00EC))needs to generate backtick `
//dovered by doubleclicking the script exe. 
//Virtual key: DD  Scan key: 00D literal: ì
<^>!SC00D::
SendInput, ~
return

//trailing end is important!