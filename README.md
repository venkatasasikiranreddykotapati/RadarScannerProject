# Radar-Room-Scanner

A project to build a 2D room scanner using an FMCW radar on a PSoC 6 MCU, with all high-level processing done in Python.

## Project Structure

The project is divided into two main parts:
1.  **Firmware:** A C/C++ application that runs on the PSoC 6 MCU to handle real-time data acquisition.
2.  **Python Application:** A Python-based system that runs on a PC to orchestrate data collection, processing, mapping, and visualization.

## Setup

### 1. Firmware
Follow the instructions in `firmware/flashing_instructions.md` to build and flash the correct firmware to your board. This is a **required one-time step**.

### 2. Python Environment
It is recommended to use a `conda` environment.

```sh
conda create -n radar-scanner python=3.11
conda activate radar-scanner
pip install -r requirements.txt
```

### 3. Running the Application
Once the firmware is flashed and the Python environment is set up, you can run the main application:

```sh
python src/main.py
```
