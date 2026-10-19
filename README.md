## Installation

### 1. Check Python

Make sure Python 3 is installed:

```bash
python3 --version
```

### 2. Install Scapy

Install the required Python package:

```bash
python3 -m pip install scapy
```

### 3. Verify Scapy

Check whether Scapy is installed correctly:

```bash
python3 -c "import scapy; print('Scapy installed successfully!')"
```

### 4. Install from requirements.txt

Alternatively, install all project dependencies using:

```bash
python3 -m pip install -r requirements.txt
```

### 5. Run the Analyzer

Start the network packet analyzer using:

```bash
python3 packet_analyzer.py
```

The program will capture network packets and display:

* Packet number
* Source IP address
* Destination IP address
* Protocol
* Source port
* Destination port
* Packet size
* Total packets captured
# NetworkPacketAnalyzer
