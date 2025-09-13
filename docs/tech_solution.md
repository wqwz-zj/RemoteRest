# 高通骁龙8295 主控 智能座舱系统技术方案（概要）

> 说明：本文件为工程级技术方案草案，供立项评审、硬件/软件团队开展详细设计使用。由于 Qualcomm 之类的 SoC 引脚表和某些设计资料为厂商保密数据，本方案以公开可用信息与工程建议为主，实际 PCB/引脚级设计请与 Qualcomm / 方案提供方签署 NDA 后获取官方 reference design 与 pinmux table。

## 一、项目概述
- 主控：Qualcomm Snapdragon 8295 SoC（下称 8295）
- 目标：智能座舱平台，支持 9 块 2K 显示屏（中控 3 连屏、后排 2×、流媒体后视镜、外后视镜显示、前排副驾屏），千兆以太网通信与诊断（DoIP/UDS）、娱乐、Wi‑Fi、BT、5G、OTA、疲劳预警、人脸识别、23 声道音频、导航、空调/座椅控制等车载功能。

## 二、主要功能点
- 显示：9×2K 屏，多路输出（MIPI‑DSI/eDP/LDVS/HDMI/DP/外置视频分配器）
- 视觉：360 摄像头输入（GMSL/FPD‑Link/MIPI CSI）、内部人脸与疲劳摄像头
- 音频：23 路扬声器驱动（I2S/TDM → DSP → 多通道功放），主/副驾麦克风阵列、AEC/NR
- 网络：千兆以太网交换机 + PHY（车规），千兆 DoIP 诊断，5G 模块（M.2/PCIe），Wi‑Fi/BT
- 系统软件：Android（AOSP/车载 Android）为上层，底层驱动 C/C++ 实现，应用/服务使用 Java/Kotlin 与 Python
- 诊断：UDS (ISO 14229) over DoIP (ISO 13400)，远程诊断通过 TLS+mTLS + MQTT/HTTPS
- OTA：A/B 双分区或双镜像，签名校验、回滚、差分更新

## 三、系统框图（文本版）
```
[5G Module]--PCIe/USB--+
[WiFi/BT]--PCIe/SDIO----|          +--Display Panels (9x 2K)
[GPS]----UART/I2C-------|--[Ethernet Switch]--[Ethernet PHYs]--[Car Net]
[Camera Deserial]--MIPI-|          |--Audio Codec/DSP--Amplifiers--Speakers(23)
                       [Snapdragon 8295 SoC]
                       |--LPDDR5
                       |--UFS
                       |--PCIe (5G)
                       |--MIPI‑DSI/CSI
                       |--USB3.0 / HDMI
                       |--I2S/TDM
                       |--Secure Boot / TEE
```

## 四、硬件接口清单（概要）
- 显示接口：MIPI‑DSI、eDP、LVDS/LDVS、HDMI、DisplayPort
- 摄像头接口：GMSL / FPD‑Link → Deserializer → MIPI‑CSI
- 音频接口：I2S / TDM / I2C (codec ctrl) / speaker outputs
- 网络接口：Ethernet Switch + 1Gb PHYs（RJ45 或 1000BASE‑T1 PHY）
- 外设：USB3.0 / USB2.0, PCIe x1, SDIO, CAN / LIN（via transceiver）
- 天线：5G / Wi‑Fi/BT / GPS / FM

## 五、软件架构（概要）
- Bootloader (secure boot) -> Kernel -> init -> native daemons & Android framework
- Native daemons: diagnosticsd (DoIP/UDS), cameradm (vision pipeline), audiomgrd, npu_agent, networkd, ota_agent
- HAL: Display HAL, Camera HAL, Audio HAL, Network HAL (C/C++)
- Android layer: System Server, HMI App, Media Player, Navigation

## 六、诊断协议（摘要）
- 本地诊断：UDS (ISO 14229) 服务集合，通过 DoIP (ISO 13400) 在以太网上承载
- 远程诊断：使用 TLS+mTLS + MQTT/HTTPS 与云端交互，云端可下发诊断任务并通过安全隧道与车端 agent 协同
- 权限：分级安全访问，使用 UDS 0x27 challenge/response，与 TEE 集成保管密钥

## 七、BOM 样例与关键器件
- SoC: Qualcomm Snapdragon 8295（与 Qualcomm 对接确认）
- LPDDR5 16GB: Samsung / SKHynix
- UFS 256GB: Samsung
- Ethernet switch: Marvell / Microchip（按端口数）
- 5G Module: Quectel / Fibocom (PCIe M.2)
- WiFi/BT module: Broadcom/Qualcomm combo
- GNSS module: u‑blox NEO‑M9N
- Camera SerDes: Maxim / TI
- Audio codec / amp: Cirrus Logic / TI

## 八、交付物清单（本次交付）
- 本技术方案文档（Markdown）
- 示例代码骨架：Display HAL (C), OTA Agent (Python), diagnosticsd (Python skeleton)
- BOM CSV 模板
- 给 Qualcomm 的对接邮件模板

## 九、后续工作建议
1. 与 Qualcomm 签署 NDA 并获取 8295 reference design 与 pinmux table
2. 硬件原理图绘制（Altium/Allegro），关键差分线/电源网络仿真
3. 首版 PCB 制作与 Bring‑up
4. 内核驱动、HAL 与中间件并行开发

---
*注：若需要我把本次交付的文件推送到您的仓库 feature/8295-ivi 分支，我会尝试在该分支提交这些文件；若我没有写权限，我会把完整的 git 命令与打包文件发送给您以便本地推送。*