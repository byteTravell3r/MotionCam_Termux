# MotionCam_Termux
**A Simple Security Camera with Motion Detection implemented with Python3, Termux:API, OpenCV and rsync**

## What can it do?
1. Takes photoes using the phone's built-in (rear or front) camera and LED flash light.
2. Detects if there's any difference between two picture frames and save them selectively.
3. Upload the photoes to any device capable of running SSH and SFTP server (and with enough storage space).

## Future plans
1. Add timestamp mark to the photoes. (Now timestamp is in the filename only.)
2. Support timing with RTC (For example, remove the photoes from remote computer monthly.)
3. ... ...

## Pre-requisities
1. An Android Phone (better with root privilege)
2. Install **Termux** and **Termux:API** from F-Droid or GitHub (optional: **Termux:Boot**, **SmartPack Kernel Manager**)
3. In **Termux** run:
   `pkg install openssh python3 opencv-python rsync libjpeg-turbo libtiff termux-api`
5. Generate an SSH key of your phone(with `ssh-keygen`) then upload the pubkey to remote server (file: `~/.ssh/authorized_keys`)
6. `ssh` connect your phone to the desired remote server once (for `known_hosts yes`)
7. (Optional) Set the CPU governor to "**performance**" (in "**SmartPack Kernel Manager**" or other similar Apps), add this script to **Termux:Boot**
8. Upload this script to Termux home directory (using `ssh` or anything else you like)
9. Make this script executable: `chmod +x motioncam.py`

## Running
### Parameters
   It is pretty much self-explained.
   `./motioncam.py [-l --light] [-r --rsync] [-m --motion] [-c --count]`
1. `--light`: Enable Camera LED Flash Light.
2. `--rsync`: Enable Incremental Sync (rsync).
3. `--motion`: Enable Motion Detection.
4. `--count`: Auto Sync Frequency (Upload Per (x) Valid Shots)


