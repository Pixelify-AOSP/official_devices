<p align="center">
  <img src="https://raw.githubusercontent.com/ASCP-staging/official_devices/17/assets/banners/latest.png" alt="ASCP OS Banner" width="800" />
</p>

# <p align="center">🔮 ASCP OS — Official Devices & OTA Hub</p>

<p align="center">
  <img src="https://img.shields.io/badge/Android-17_/_A17-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android Version" />
  <img src="https://img.shields.io/badge/ASCP_OS-v6.0-6C5CE7?style=for-the-badge" alt="ASCP OS Version" />
  <img src="https://img.shields.io/badge/STATUS-ACTIVE-2ECC71?style=for-the-badge" alt="Status" />
</p>

---

Welcome to the central repository for **ASCP OS** official devices, OTA configuration database, and changelog updates. 

---

## 📱 Official Roster

The following devices are officially supported, receiving automated OTA system updates, recovery integration, and dedicated maintenance support:

| Device Model | Codename | Maintainer | Support Link |
|:---|:---:|:---|:---:|
| **Poco F5 / Redmi Note 12 Turbo** | `marble` | [![Ashwani](https://img.shields.io/badge/Ashwani-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/beingashwani) | [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/being_ashwani) |
| **Redmi Turbo 3 / POCO F6** | `peridot` | [![kenway214](https://img.shields.io/badge/kenway214-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/kenway214) | [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/ph12nex) |
| **CMF Phone 1** | `Tetris` | [![Anshuman X](https://img.shields.io/badge/Anshuman%20X-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/maxxcodebug) | [![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/AnshumanAhirwar) |
| **OnePlus Nord CE 3 Lite** | `larry` | [![NoEscape.exe](https://img.shields.io/badge/NoEscape.exe-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/n0escape-exe) | [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/n0escape_exe) |
```

## 🚀 Guidelines for Maintainership

Interested in bringing official ASCP OS support to your device? 

1. **Stability First**: Devices must boot reliably, pass CTS/Play Integrity out-of-the-box, and run without major functionality regressions.
2. **Commitment**: Maintainers are expected to keep their builds updated with monthly security patches.
3. **Clean Code**: Tree sources must be public and cleanly tracked on our organization's GitHub.

> **💡 OTA Delivery**: Once your device is accepted, updates are configured via the `devices.json` database in this repository. Ensure your device updater configuration is validated by the JSON lint workflow before PR submission.
