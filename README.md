# GloveMouse – Wearable Bluetooth HID Mouse

A custom-designed wearable glove mouse that combines **motion control**, **macro input**, and **haptic feedback** to enhance user interaction and replace traditional mice for hands-free computing or accessibility solutions.

## 🔧 Overview

GloveMouse is an all-in-one wearable device powered by an **ESP32** microcontroller that functions as a **Bluetooth HID** device, acting as both a mouse and a keyboard. It detects hand gestures using a gyroscope and sends corresponding cursor movement or macro commands via BLE. The project integrates various peripherals for input and feedback, allowing a fully interactive user experience.

## 🎯 Features

- **Gyroscope-Based Motion Control**  
  Move the mouse cursor by tilting your hand.

- **T9 Keypad Input System**  
  Enter text using a numeric keypad layout with multi-tap detection logic.

- **Macro Triggering via Motion**  
  Specific directional gestures send keyboard shortcuts to the connected PC.

- **Rotary Encoder for Mouse Wheel**  
  Emulates scroll wheel behavior for natural navigation.

- **Feedback System**  
  - **RGB LED** indicates connection status and user interaction.  
  - **OLED Display** provides visual prompts and mode information.  
  - **Buzzer** and **vibration motor** offer audio and tactile feedback.

- **BLE HID Implementation**  
  Seamless connection with any Bluetooth-enabled computer without additional drivers.

## ⚙️ Hardware Used

- **ESP32-WROOM-32E** microcontroller  
- **MPU6050 gyroscope**  
- **Rotary encoder switch**  
- **Tactile buttons (T9 layout)**  
- **SSD1306 OLED Display**  
- **Mini vibration motor**  
- **Piezo buzzer**  
- **Custom-designed PCB**

## 🛠️ Software Stack

- **MicroPython** for embedded control  
- **BLE HID libraries** for mouse/keyboard emulation  
- **Custom Python PC-side macro listener** (optional)  
- **Fusion 360** for PCB and mechanical design

## 📸 Concept Rendering

![Concept Rendering](/Concept_Renderings/concept_1.jpg)


## 📦 Status

This project was successfully completed and featured in the **Seneca Engineering Showcase 2025**. All hardware components are fully integrated and functional in a wearable glove format.

---

Want to use this project or contribute? Fork it, study the code, or reach out!
