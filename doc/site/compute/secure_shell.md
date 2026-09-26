# Secure Shell

[Secure SHell](https://ssh.com/academy/ssh) (SSH) is a cryptographic network
protocol, that is commonly used execute commands on a server. SSH secures
communication using keys.

## Key Generation

SSH keys can be generated with several cryptosystem algorithms. Ed25519 is
considered of the more secure algorithms. The following commands will generate
passphraseless private and public keys using Ed25519 for Unix systems.

```bash
# Create SSH directory with correct permissions.
#
# Flags:
#     -p: Make parent directories as needed.
#     -m 700: Give all permission to current user and no permissions to other users.
mkdir -p -m 700 "$HOME/.ssh"

# Generate SSH private and public keys.
#
# Flags:
#     -q: Silence ssh-keygen.
#     -N '': Do not associate a password with the key.
#     -f path: Filename of the key file.
#     -t ed25519: Use Ed25519 key signature algorithm.
#     -C email: Specify user host comment in public key.
ssh-keygen -N '' -q -f "$HOME/.ssh/keyname" -t ed25519 -C username@mailhost.com

chmod 600 "$HOME/.ssh/keyname"
```

The following PowerShell commands will generate passphraseless private and
public keys using Ed25519 for Windows systems.

```powershell
ssh-keygen -q -N '' -f "$HOME/.ssh/keyname" -t ed25519 -C username@mailhost.com
```

## TTY Allocation

The remote login shell can be changed with the `-t` flag. For example, the Fish
shell can be used with command `ssh -t username@hostname fish`.

## Configuration

### User

SSH can be configured for a user with the following file template.

_$HOME/.ssh/config_

```
# SSH configuration file.
#
# For more information, see https://ssh.com/ssh/config.

Host *
    # Use only IdentityFile key for each host.
    IdentitiesOnly yes
    Port 22

Host github.com
    HostName domain_name
    IdentityFile private_key_path
    User git_user
```

### System

For the system configuration, the file exists at `/etc/ssh/sshd_config` on Unix
systems and at `C:\ProgramData\ssh\sshd_config` on Windows. It is recommended to
add the following lines to the file:

```
PasswordAuthentication no
```

To relaunch the SSH daemon after changing the system configuration, execute the
associated command for your system.

- Linux: `sudo systemctl restart sshd`
- MacOS: `sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist`
- Windows: `Restart-Service sshd`

## Continuous Integration

Using SSH in continuous integration pipelines can tricky, since keys are
commonly stored in protected environment variables rather in files on disk. The
following sections show how integrate SSH with only environment variables for
specific use cases.

### Execute Remote Commands

Execute a shell command on a remote server.

```bash
# Install OpenSSH client.
sudo apt-get update -q
sudo apt-get -qy openssh-client

# Launch the SSH key manager.
#
# Flags:
#   -s: Generate Bourne shell commands on stdout.
eval "$(ssh-agent -s)"

# Add SSH private key to SSH agent via piping.
ssh-add <(echo "${SSH_PRIVATE_KEY}")

# Connect to remote computer via SSH and execute command.
#
# Flags:
#   -o IdentitiesOnly=no: Allow for identities not specified in the SSH config.
#   -o StrictHostKeyChecking=no: Allow for unknown hosts.
#   -o UserKnownHostsFile=/dev/null: Do not update known hosts file.
ssh -o IdentitiesOnly=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null username@hostname command
```

### Remote Docker Context

Launch a Docker container on a remote server.

```bash
# Install OpenSSH client.
sudo apt-get update -q
sudo apt-get -qy openssh-client

# Launch the SSH key manager.
#
# Flags:
#   -s: Generate Bourne shell commands on stdout.
eval "$(ssh-agent -s)"

# Add SSH private key to SSH agent via piping.
ssh-add <(echo "${SSH_PRIVATE_KEY}")

# Create SSH configuration directory with required permissions.
mkdir -p -m 700 "${HOME}/.ssh"

# Update known hosts file with remote computer SSH public key.
ssh-keyscan hostname.com 1>> "${HOME}/.ssh/known_hosts" 2>/dev/null

# Create remote context if it does not already exist.
if [[ ! "$(docker context inspect remotename)" ]]; then
  docker context create --docker "host=ssh://username@hostname" remotename
fi

# Deploy Docker container on remote computer.
docker --context remotename run -dit image:tag
```

## MacOS

MacOS does not allow inbound SSH connections by default. To enable inbound SSH
connections, execute `sudo systemsetup -setremotelogin on` after enabling _Full
Disk Access_ for the _sshd-keygen-wrapper_ in the _Privacy & Security_ settings.

## Windows

Microsoft includes the OpenSSH client on newer versions of Windows by default.
However, the OpenSSH server is an optional feature that is not enabled by
default. To install and configure an OpenSSH server, execute the following
commands.

```powershell
# Add SSH server feature to Windows.
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start the OpenSSH daemon.
Start-Service sshd

# Make the OpenSSH daemon start on system startup.
Set-Service -Name sshd -StartupType 'Automatic'

# Open Windows firewall to allow connections on port 22.
New-NetFirewallRule -Action Allow -Direction Inbound -DisplayName 'OpenSSH Server' -Enabled True -LocalPort 22 -Name sshd -Protocol TCP

# Set PowerShell as login shell for SSH connections.
New-ItemProperty -Force -Name DefaultShell -Path 'HKLM:\SOFTWARE\OpenSSH' -PropertyType String -Value 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
```

For more information, visit
https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse.

### Adding Keys

For nonadministrative users, a public key can be added in the standard
`$HOME/.ssh/authorized_keys` file. However, for administrative users, the public
key must be added to the `C:\ProgramData\ssh\administrators_authorized_keys`
file and the following command must be run afterwards.

```powershell
icacls.exe 'C:\ProgramData\ssh\administrators_authorized_keys' /inheritance:r /grant 'Administrators:F' /grant 'SYSTEM:F'
```

## Proxy Usage

Connect to a publically inaccessible target via a gateway proxy.

```
ssh -o ProxyCommand="ssh -i ~/.ssh/proxykey -W %h:%p proxyuser@proxyhost" -i ~/.ssh/targetkey targetuser@targethost
```
