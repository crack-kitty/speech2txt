[Setup]
AppName=Speech2Txt
AppVersion=1.2.0
AppPublisher=Speech2Txt
DefaultDirName={autopf}\Speech2Txt
DefaultGroupName=Speech2Txt
UninstallDisplayIcon={app}\Speech2Txt.exe
OutputDir=installer
OutputBaseFilename=Speech2Txt-Setup
SetupIconFile=assets\speech2txt.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "dist\Speech2Txt.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Speech2Txt"; Filename: "{app}\Speech2Txt.exe"; IconFilename: "{app}\Speech2Txt.exe"
Name: "{group}\Uninstall Speech2Txt"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Speech2Txt"; Filename: "{app}\Speech2Txt.exe"; IconFilename: "{app}\Speech2Txt.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Speech2Txt.exe"; Description: "Launch Speech2Txt"; Flags: nowait postinstall skipifsilent
