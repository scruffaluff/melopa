# File System

## Background

Management of computer storage on disks can be summarized by the following list
of ascending abstractions.

- Drive
- Partition
- Volume
- File System

Computer disk/drive hardware is divided into referenceable sections called disk
sectors, which are its smallest storage units. Drives are often formatted into
regions called partitions. Each partition is a contiguous area of the disk which
can be managed as a separate disk by software. A drive's partition information
is stored in a partition table located at the beginning of the disk. The two
most used partition tables are the Master Boot Record (MBR) and the GUID
Partition Table (GPT). An operating system will mount a combination of disk
partitions from a set of disks as a volume.

To view the partitions and volumes on a Linux system execute `sudo fdisk --list`
or `sudo lsblk`.

## Purpose

An operating system uses a file system to manage the data from a volume. To
avoid fragmentation, file systems divide a volume into virtual compartments
called clusters. A cluster is a contiguous set of disk sectors. A file system
maintains an index describing file locations and available free space. Some file
systems use journaling to record changes and support recovery in case of
corruption.

## Btrfs

Btrfs is a copy on write file system with a built-in logical volume manager.

## FAT

The File Allocation Table (FAT) is a legacy with the following widely supported
variants.

- FAT32: 32bit extension to VFAT
- VFAT: Extension to FAT with support for file names with up to 255 characters.
- exFAT: 64bit extension to FAT. Stands for extensible File Allocation Table.

## ZFS

The Zettabyte File System (ZFS) is commonly used in Network Attached Storage
(NAT) devices.

## Docker

Docker uses the Overlay File System (OverlayFS).

## Linux

Linux most commonly uses the 4th version of Extended File System (ext4) for its
root file system at `/`. Linux also commonly mounts additional file systems at
the following locations.

- `/boot`: Contains all files necessary to boot the operating system. Usually is
  a separate file system from `/` since `/boot` cannot be encrypted.
- `/boot/efi`: FAT32 UEFI variant file system with bootloader, device, and
  kernel programs for UEFI firmware to use at boot time.
- `/run/user/1000`: Temporary storage location for user 1000's running programs.
  Alternative to `/tmp` storage that isn't writable by programs running under
  different users.

### FSTAB

Most Unix systems specify their file system mount in the file systems table file
`/etc/fstab`, which has the following layout.

```
# device-spec mount-point fs-type options   dump pass
/dev/sda1     /           ext4    defaults  0    1
```

- `device-spec` is the storage device's mount path or `key=value` label. It is
  recommended to use `UUID=DEVICES-SPECIFIC-UUID` so that if the storage device
  is remounted at a different location fstab will remount the file system
  correctly. The UUID of a storage device can be found with the command
  `blkid -s UUID -o value /dev/devices-name`.
- `options` is a comma separated list of `key=value` pairs to send to file
  system software. The key `defaults` specifies that the file system should use
  its built-in default options.
- `dump` specifies whether the `dump` program should automatically back up the
  file system. Since `dump` is outdated, the value should always be 0.
- `pass` specifies the `fsck` order for checking errors at boot time. It is
  recommended to set value 1 for the root file system, and value 2 for other
  file systems.

After editing the `/etc/fstab`, all of its mounts can be launched with the
`mount -a` command.

### LVM

The Linux Logical Volume Manager (LVM) is device mapper framework to map
physical block devices onto virtual block devices. It uses the following
abstractions, sorted in ascending order.

- Physical volume
- Volume group
- Logical volume
- File System

The Linux LVM provides commands for user configuration.

- Add partition to group: `sudo vgextend <group> <partition>`
- Upgrade volume to 256GB of space:
  `sudo lvextend --resizefs --size 256G <logical-volume>`
- Add all remaining space in group to volume:
  `sudo lvextend --resizefs --extents +100%FREE <logical-volume>`

For example on Ubuntu, the root logical volume might only be using half of the
available disk space. To fix the issue, execute
`sudo lvextend --resizefs --extents +100%FREE ubuntu-vg/ubuntu-lv`.

### XDG

The
[base directory specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
defines environment variables to unify where types of user data should be
stored.

| Variable         | Default                  | Contains                         |
| ---------------- | ------------------------ | -------------------------------- |
| $XDG_DATA_HOME   | $HOME/.local/share       | user data files                  |
| $XDG_CONFIG_HOME | $HOME/.config            | user configuration files         |
| $XDG_STATE_HOME  | $HOME/.local/state       | user state files                 |
| $XDG_CACHE_HOME  | $HOME/.cache             | user non-essential files         |
| $XDG_RUNTIME_DIR | /run/user/$(id -u $USER) | user non-essential runtime files |

## MacOS

MacOS uses the Apple File System (APFS).

## Windows

Windows uses the New Technology File System (NTFS).
