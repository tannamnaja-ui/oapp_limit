#define MyAppName "ระบบจำกัดนัดคลินิก"
#define MyAppNameEn "oapp_limit"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "oapp_limit"
#define MyAppURL "https://github.com/imhosxp4-byte/oapp_limit"
#define MyAppExeName "launcher.vbs"
#define InstallDir "{pf}\oapp_limit"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={#InstallDir}
DefaultGroupName={#MyAppName}
OutputDir=d:\PROJECT-BMS\oapp_limit\_output
OutputBaseFilename=Oapp-Limit-Full
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={#InstallDir}\launcher.vbs
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create Desktop Shortcut"; GroupDescription: "Additional options:"

[Files]
; App files
Source: "d:\PROJECT-BMS\oapp_limit\server.js";         DestDir: "{app}"; Flags: ignoreversion
Source: "d:\PROJECT-BMS\oapp_limit\package.json";       DestDir: "{app}"; Flags: ignoreversion
Source: "d:\PROJECT-BMS\oapp_limit\package-lock.json";  DestDir: "{app}"; Flags: ignoreversion
Source: "d:\PROJECT-BMS\oapp_limit\config.py";          DestDir: "{app}"; Flags: ignoreversion
Source: "d:\PROJECT-BMS\oapp_limit\db_config.json";     DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "d:\PROJECT-BMS\oapp_limit\static\*";           DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "d:\PROJECT-BMS\oapp_limit\views\*";            DestDir: "{app}\views";  Flags: ignoreversion recursesubdirs createallsubdirs
Source: "d:\PROJECT-BMS\oapp_limit\templates\*";        DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "d:\PROJECT-BMS\oapp_limit\node_modules\*";     DestDir: "{app}\node_modules"; Flags: ignoreversion recursesubdirs createallsubdirs
; Launcher & stop scripts
Source: "d:\PROJECT-BMS\oapp_limit\_installer\launcher.vbs";     DestDir: "{app}"; Flags: ignoreversion
Source: "d:\PROJECT-BMS\oapp_limit\_installer\stop_server.vbs";  DestDir: "{app}"; Flags: ignoreversion
; Node.js installer (bundled for offline install)
Source: "d:\PROJECT-BMS\oapp_limit\_installer\node-setup.msi";   DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\{#MyAppName}";                  Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs""";     WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 14
Name: "{group}\หยุดเซิร์ฟเวอร์";              Filename: "{sys}\wscript.exe"; Parameters: """{app}\stop_server.vbs""";  WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 131
Name: "{group}\ถอนการติดตั้ง {#MyAppName}";   Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";             Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs""";     WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 14; Tasks: desktopicon

[Run]
; Install Node.js silently if not present
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\node-setup.msi"" /qn /norestart ADDLOCAL=ALL"; Check: not IsNodeInstalled; StatusMsg: "กำลังติดตั้ง Node.js..."; Flags: waituntilterminated
; Refresh PATH
Filename: "{sys}\cmd.exe"; Parameters: "/c setx PATH ""%ProgramFiles%\nodejs;%PATH%"" /M"; Flags: runhidden waituntilterminated; Check: not IsNodeInstalled

[UninstallRun]
Filename: "{sys}\wscript.exe"; Parameters: """{app}\stop_server.vbs"""; Flags: runhidden waituntilterminated

[Code]
function IsNodeInstalled: Boolean;
var
  NodePath: String;
begin
  Result := RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SOFTWARE\Node.js',
    'InstallPath', NodePath) or
    FileExists('C:\Program Files\nodejs\node.exe') or
    FileExists('C:\Program Files (x86)\nodejs\node.exe');
end;

function InitializeSetup: Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Write default db_config.json if not exists
    if not FileExists(ExpandConstant('{app}\db_config.json')) then
    begin
      SaveStringToFile(ExpandConstant('{app}\db_config.json'),
        '{"active":"mysql","mysql":{"host":"localhost","port":3306,"database":"","username":"","password":""},"postgresql":{"host":"localhost","port":5432,"database":"","username":"","password":""}}',
        False);
    end;
  end;
end;
