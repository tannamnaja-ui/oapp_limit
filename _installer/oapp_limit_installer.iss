#define MyAppName "ระบบจำกัดนัดคลินิก"
#define MyAppNameEn "Oapp-Limit"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "HOSxP"
#define MyAppURL "https://github.com/imhosxp4-byte/oapp_limit"
#define AppRoot "..\"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567891}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\Oapp-Limit
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=Oapp-Limit-Full
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
; ลบเวอร์ชันเก่าก่อนติดตั้งใหม่
CloseApplications=yes
CloseApplicationsFilter=*node*,*wscript*
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "สร้าง Shortcut หน้า Desktop"; GroupDescription: "เพิ่มเติม:"; Flags: checked

[Files]
; App source files
Source: "{#AppRoot}server.js";           DestDir: "{app}"; Flags: ignoreversion
Source: "{#AppRoot}package.json";         DestDir: "{app}"; Flags: ignoreversion
Source: "{#AppRoot}package-lock.json";    DestDir: "{app}"; Flags: ignoreversion
Source: "{#AppRoot}config.py";            DestDir: "{app}"; Flags: ignoreversion
Source: "{#AppRoot}main.py";              DestDir: "{app}"; Flags: ignoreversion
Source: "{#AppRoot}requirements.txt";     DestDir: "{app}"; Flags: ignoreversion
Source: "{#AppRoot}static\*";             DestDir: "{app}\static";    Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#AppRoot}views\*";              DestDir: "{app}\views";     Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#AppRoot}templates\*";          DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#AppRoot}database\*";           DestDir: "{app}\database";  Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#AppRoot}ui\*";                 DestDir: "{app}\ui";        Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#AppRoot}node_modules\*";       DestDir: "{app}\node_modules"; Flags: ignoreversion recursesubdirs createallsubdirs
; VBScript launchers (ไม่มี command prompt)
Source: "{#AppRoot}_installer\launcher.vbs";    DestDir: "{app}"; Flags: ignoreversion
Source: "{#AppRoot}_installer\stop_server.vbs"; DestDir: "{app}"; Flags: ignoreversion
; Node.js offline installer
Source: "{#AppRoot}_installer\node-setup.msi";  DestDir: "{tmp}"; Flags: deleteafterinstall
; Icon
Source: "{#AppRoot}_installer\icon.ico";        DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Start Menu
Name: "{group}\เปิดโปรแกรม";             Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"
Name: "{group}\หยุดเซิร์ฟเวอร์";         Filename: "{sys}\wscript.exe"; Parameters: """{app}\stop_server.vbs"""; WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 131
Name: "{group}\ถอนการติดตั้ง";           Filename: "{uninstallexe}"
; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}";       Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
; ติดตั้ง Node.js ถ้ายังไม่มี (ข้ามถ้ามีแล้ว)
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\node-setup.msi"" /qn /norestart ADDLOCAL=ALL"; Check: not IsNodeInstalled; StatusMsg: "กำลังติดตั้ง Node.js..."; Flags: waituntilterminated
Filename: "{sys}\cmd.exe"; Parameters: "/c setx PATH ""%ProgramFiles%\nodejs;%PATH%"" /M"; Flags: runhidden waituntilterminated; Check: not IsNodeInstalled
; เปิดโปรแกรมหลังติดตั้ง
Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; WorkingDir: "{app}"; Description: "เปิดโปรแกรม"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\wscript.exe"; Parameters: """{app}\stop_server.vbs"""; Flags: runhidden waituntilterminated

[Code]
function IsNodeInstalled: Boolean;
begin
  Result :=
    FileExists('C:\Program Files\nodejs\node.exe') or
    FileExists('C:\Program Files (x86)\nodejs\node.exe') or
    RegValueExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Node.js', 'InstallPath') or
    RegValueExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Node.js', 'InstallPath');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if not FileExists(ExpandConstant('{app}\db_config.json')) then
    begin
      SaveStringToFile(ExpandConstant('{app}\db_config.json'),
        '{"active":"mysql","mysql":{"host":"localhost","port":3306,"database":"","username":"","password":""},' +
        '"postgresql":{"host":"localhost","port":5432,"database":"","username":"","password":""}}',
        False);
    end;
  end;
end;
