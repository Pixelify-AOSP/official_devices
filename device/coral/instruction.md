**CLEAN FLASH IS RECOMMEND**

Requirement: 
1. Upgrade final version from stock Android (Android 13).
2. Ensure device unlocked bootloader

Flashing Instruction
1. Reboot to Bootloader
2. Flash boot
```bash
fastboot flash boot boot.img
```
3. Reboot to recovery → Apply Update → Apply from ADB
4. On the host machine, sideload package using:
```bash
adb -d sideload /path/to/zip
```
5. Reboot and Enjoy!
