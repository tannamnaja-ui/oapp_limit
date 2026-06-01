#define MyAppName "Oapp-Limit"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "HOSxP"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567892}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Oapp-Limit
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=Oapp-Limit-Full
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: desktopicon; Description: "Create Desktop Shortcut"; GroupDescription: "Options:"

[Files]
Source: "..\server.js";             DestDir: "{app}"; Flags: ignoreversion
Source: "..\package.json";           DestDir: "{app}"; Flags: ignoreversion
Source: "..\package-lock.json";      DestDir: "{app}"; Flags: ignoreversion
Source: "..\config.py";              DestDir: "{app}"; Flags: ignoreversion
Source: "..\main.py";                DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt";       DestDir: "{app}"; Flags: ignoreversion
Source: "..\static\*";               DestDir: "{app}\static";    Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\views\*";                DestDir: "{app}\views";     Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\templates\*";            DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\database\*";             DestDir: "{app}\database";  Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\ui\*";                   DestDir: "{app}\ui";        Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\node_modules\*";         DestDir: "{app}\node_modules"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: ".\launcher.vbs";    DestDir: "{app}"; Flags: ignoreversion
Source: ".\stop_server.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\node-setup.msi";  DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\Open {#MyAppName}";     Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; WorkingDir: "{app}"
Name: "{group}\Stop Server";           Filename: "{sys}\wscript.exe"; Parameters: """{app}\stop_server.vbs"""; WorkingDir: "{app}"
Name: "{group}\Uninstall";             Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";    Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\node-setup.msi"" /qn /norestart ADDLOCAL=ALL"; Check: not IsNodeInstalled; StatusMsg: "Installing Node.js..."; Flags: waituntilterminated
Filename: "{sys}\cmd.exe"; Parameters: "/c setx PATH ""%ProgramFiles%\nodejs;%PATH%"" /M"; Flags: runhidden waituntilterminated; Check: not IsNodeInstalled
Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; WorkingDir: "{app}"; Description: "Launch application"; Flags: nowait postinstall skipifsilent

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
