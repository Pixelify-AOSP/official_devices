# 21-Jan-2026
- Fix 5g vonr on jio
- Fix fast charging
- Update thermal from stock
- Introduce displayfeature color service and use MIUI color modes
- Set standard display color mode in AOD
- Provide MIUI color mode options
- Import QCOM audio effects from OnePlus 9R
- Enable Qualcomm TrueWireless Stereo
- Switch to Lunaris dolby
- Fix battery and USB OTG detection
- Define OEM fast charge sysfs node
- Downscale task snapshots to 80%
- Drop force triple frame buffer
- Switch to armv8-2a dotprod arch
- Fixing connecting BLE (bt 5.x) devices (smart watches, etc.)
- Relax RSSI thresholds

# 28-Dec-2025
- Add props to improve battery backup
- Optimize auto brightness adjustment
- Tune ambient display burn-in protection

# 16-Dec-2025
- Synced with latest qpr1 source
- enabled the 1k nits brightness by default
- Some mics changes in boosts
- Disable Lift to check by default
- Partially import parts from sm8350-common:
* Thermals
* Per-app refresh rate
* Clear speaker
* Doze
- Force enable volte and wifi calling
- Fixed USSD dial issue
- Enabled 120Hz Keyguard
- Optimize SurfaceFlinger properties for graphics performance(This should improve graphics performance, smoothness, and screen responsiveness)
- Add Gcam by default
