# Troubleshoot

- To increase the command line `sudo` authentication timeout to 60 minutes, add
  the line `Defaults timestamp_timeout=60` to the file `/etc/sudoers`.

## MacOS

- To disable _Developer Tools Access_ popups during lldb debugging, execute
  `sudo /usr/sbin/DevToolsSecurity --enable`.
- To disable the blue caps lock indicator execute the following commands and
  restart the computer.
  ```
  sudo mkdir -p /Library/Preferences/FeatureFlags/Domain
  sudo /usr/libexec/PlistBuddy -c "Add 'redesigned_text_cursor:Enabled' bool false" /Library/Preferences/FeatureFlags/Domain/UIKit.plist
  ``
  ```
- To disable warning prompts on MacOS when opening an executable file downloaded
  from a browser, execute `xattr -d com.apple.quarantine <file>`. For more
  information, visit https://superuser.com/a/28400.
- To enable fingerprint authentication for sudo on MacOS, add the line
  `auth sufficient pam_tid.so` to the file `/etc/pam.d/sudo_local`. For more
  information, visit https://apple.stackexchange.com/a/466029.
