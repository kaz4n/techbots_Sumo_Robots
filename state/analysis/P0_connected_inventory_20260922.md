# Connected UNO Q local inventory — 2026-09-22

Observed 22:54–22:56 Asia/Dubai. Bounded read-only local inventory after the user
reported the UNO Q connected with no external hardware and supplied a Windows
Arduino CLI in this checkout. Read FACTS, docs/P0_MANUAL_CHECKLIST.md,
tools/README.md and tools/preflight.sh before discovery. No upload, compile,
reset, firmware start, package installation, board shell, arbitrary LAN-host
connection or credential-file access occurred. No credentials were used or saved.
This report changes no source, FACTS ledger, pin assignment or phase gate.

## Identified target

The Windows USB device and CLI USB/network discovery agree on serial
`2629958581`. This is the explicitly identified target for subsequent separately
scoped work; no first-device assumption is needed.

| Observation | Actual result |
|---|---|
| USB parent | `USB\VID_2341&PID_0078\2629958581`, status OK |
| USB product descriptor | `UNO Q - Tarek` |
| Serial interface | COM10, `USB\VID_2341&PID_0078&MI_01\6&1A1D8642&0&0001`, status OK |
| ADB interface | `USB\VID_2341&PID_0078&MI_00\6&1A1D8642&0&0000`, status OK |
| CLI matching board | Arduino UNO Q, `arduino:zephyr:unoq` |
| CLI network advertisement | `Tarek.local.`, `192.168.1.120`, serial_number `2629958581` |
| Network metadata | protocol network; distro_version 0.1, advertised port 80, auth_upload yes, ssh_upload no |
| ADB enumeration | `2629958581 device transport_id:1` |

The network metadata is an advertisement, not an authenticated board OS inventory
or proof that SSH is disabled. COM10 was enumerated only; it was not opened.
The ADB device listing does not prove an installed CLI/core, loader or firmware.

Windows signed drivers: USB serial `usbser.inf` 10.0.26100.9278; ADB `winusb.inf`
10.0.26100.9444; USB composite `usb.inf` 10.0.26100.9444, all Microsoft.
There was no present Arduino/USB Ethernet adapter. Host Wi-Fi was up at
192.168.1.206/24; other up interfaces were existing Hyper-V/WSL/VirtualBox virtual
adapters. No guessed network address was probed.

## Local tools

| Tool | Exact observation |
|---|---|
| Supplied CLI | `C:\Users\narut\OneDrive\Desktop\Project\techbots_Sumo_Robots\arduino-cli.exe` |
| Version | 1.5.2-rc.1, commit fef6e48df, build date 2026-07-23T11:13:25Z |
| File | 37,865,984 bytes; last write 2026-09-22 22:49:27 +04 |
| SHA-256 | `BA1890AFCFC08524F76191B5CC801B0779CB25E81A5E6693EB0E26B50A3F3538` |
| Bundled ADB | `%LOCALAPPDATA%\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe`; 1.0.41 / 32.0.0-8006631 |
| Android SDK ADB | `%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe`; 1.0.41 / 37.0.0-14910828; version query only |
| Existing ADB server | PID 10496, bundled 32.0.0 executable, listening at 127.0.0.1:5037 |
| Windows SSH | `C:\Windows\System32\OpenSSH\ssh.exe`; OpenSSH_for_Windows_9.5p2, LibreSSL 3.8.2 |
| WSL | Ubuntu, Linux 6.6.114.1-microsoft-standard-WSL2 |
| WSL SSH | `/usr/bin/ssh`; OpenSSH_9.6p1 Ubuntu-3ubuntu13.19, OpenSSL 3.0.13 |
| CLI/ADB PATH status | Neither on Windows PATH or WSL Ubuntu PATH; Windows explicit paths above work |
| Other discovered CLI | `C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe`; not executed |
| Windows UNO Q core | `arduino:zephyr` is not installed in the supplied CLI's current local configuration |

The existing ADB server's executable was used for device enumeration to avoid a
client/server version mismatch or restart. No adb kill-server/start-server command
was issued. Nothing was installed or added to PATH. Windows core status does not
establish the board-side installation status.

## Commands and statuses

All commands ran from the repository in PowerShell unless prefixed with WSL.

| Command / query | Status and significant output |
|---|---|
| `Get-Date -Format o` | Success; 2026-09-22, matching PLAN's setup day |
| `rg --files` scoped to Arduino/ADB/preflight/checklist/README names | Success; supplied CLI and relevant docs located |
| `Get-Content state/FACTS.md` | Success |
| Initial `Get-Content state/P0_MANUAL_CHECKLIST.md` | Failed: nonexistent path; corrected to `docs/P0_MANUAL_CHECKLIST.md`, read successfully |
| `Get-Command arduino-cli,adb,ssh,wsl -ErrorAction SilentlyContinue` | Found SSH and WSL only; explicit-path searches then found CLI/ADB above |
| `Get-PnpDevice -PresentOnly` filtered for USB, Ports, Arduino/ADB | Success; exact parent/interface identities above |
| `Get-CimInstance Win32_SerialPort` | Success; COM10 only |
| `Get-NetAdapter`, `Get-NetIPAddress -AddressFamily IPv4` | Success; local interfaces only |
| `Get-CimInstance Win32_PnPSignedDriver` filtered for VID2341/PID0078 | Success; signed drivers above |
| `Get-PnpDeviceProperty` for the exact USB parent's product/manufacturer | Success; UNO Q - Tarek |
| `Get-Item ./arduino-cli.exe`; `Get-FileHash ... -Algorithm SHA256` | Success; file metadata/hash above |
| `./arduino-cli.exe version` | Exit 0; version above |
| `./arduino-cli.exe board list --help` | Exit 0; discovery-timeout and JSON options confirmed locally |
| `./arduino-cli.exe board list --discovery-timeout 5s --json` | Exit 0; exact USB and network matches above; no error reported |
| Explicit installed ADB paths followed by `version` | Both exit 0; versions above |
| `Get-Process -Name adb`; `Get-NetTCPConnection -State Listen` filtered to 5037 | Success; existing matching bundled server above |
| Bundled ADB `devices -l` | Exit 0; one device, serial 2629958581, state device |
| `ssh -V`; `wsl -d Ubuntu -- ssh -V` | Exit 0; versions above |
| `wsl -d Ubuntu -- sh -c 'command -v arduino-cli; command -v adb; command -v ssh; uname -sr'` | Overall exit 0; CLI/ADB lookup produced no path, SSH and kernel above |
| `./arduino-cli.exe core list --json` | Exit 0; output included extensive release metadata, so repeated with JSON filtering for `arduino:zephyr`; no matching platform |
| `./arduino-cli.exe board details --fqbn arduino:zephyr:unoq --format json` | Exit 1: `Unknown FQBN: platform arduino:zephyr is not installed` |

An initial combined PowerShell table formatted later objects under the first
object's columns; the relevant inventory queries were repeated with ConvertTo-Json
and yielded the identities recorded above. Initial unfiltered core JSON exceeded
the tool output limit; the filtered check plus explicit board-details error are
the evidence for missing local zephyr, not an inference from truncated output.

## Remaining dependencies and next action

The explicit USB ADB route is available without using credentials. A subsequent
authorized read-only command can select `-s 2629958581` for board identity/tool
inventory; no board shell was opened in this task. The project SSH preflight was
not run because a verified account/host-key login has not been established in
this inventory. Board CLI/core/library/loader/router versions remain unknown.

The supplied Windows CLI does not replace the specified board-side build path;
its missing local zephyr core is not proof of a missing board core. No installation
is proposed by this report. Physical isolation is user-reported, not visually
inspected by the agent; electrical/peripheral checks remain separate. No motor
run, firmware change, physical timing result, PINMAP OK or P0 gate pass occurred.
