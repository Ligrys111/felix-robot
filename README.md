# felix-robot
Smart home + ai helper
# 🤖 Felix - Voice-Controlled Smart Light Switch

An open-source Smart Home automation project that uses a Python voice assistant ("Felix") to trigger a physical light switch via an ESP8266 (NodeMCU) and an SG90 Servo motor over WiFi.

---

## 🛠️ Hardware Requirements & Wiring

### Components:
* **NodeMCU ESP8266** development board.
* **SG90 Servo Motor** (or similar 5V micro servo).
* **Female-to-Female Jumper Wires** + 3 metal pins/needles (to bridge the female-to-female connection between the servo and jumpers).
* **Micro-USB Cable** (for power and programming).

### Wiring Diagram Table:
| SG90 Servo (Wire Color) | NodeMCU ESP8266 Pin | Description |
| :--- | :--- | :--- |
| **Brown / Black** | **G** (GND) | Ground / Common Negative |
| **Red** | **VU** (or VIN) | 5V Power directly from USB (provides the best stability) |
| **Orange / Yellow** | **D2** (GPIO 4) | PWM Signal Control |

> ⚠️ **Crucial Assembly Note:** Since both the servo plug and your jumper wires have **female** ends (holes), they cannot connect directly. You **must** insert small metal bridges (such as sewing pins, straight paperclips, or resistor legs) inside the holes to ensure a solid electrical connection. Without this, the servo will not receive power or signal!

---

## 💻 Software Setup

### 1. Arduino IDE (ESP8266)
1. Open the Arduino IDE and flash the provided `.ino` sketch to your NodeMCU.
2. Make sure to replace `WIFI SSID` and `WIFI PASSWORD` with your actual local home WiFi credentials.
3. Upload the code to the board.

### 2. How to Find the ESP8266 IP Address
1. Keep the NodeMCU connected to your computer after uploading.
2. In Arduino IDE, open the **Serial Monitor** (magnifying glass icon in the top right corner).
3. Set the baud rate speed to **115200**.
4. Press the **RST (Reset)** button on your physical NodeMCU chip.
5. You will see some system logs followed by dots (`...`), and then it will print:
   `Felix połączony z WiFi!`
   `Adres IP modułu: 192.168.X.X`
6. **Copy this IP address.** You will need it for the Python script.

---

## 🐍 Connecting Python to the ESP8266

To make your Python voice assistant communicate with the light switch, you need to route the HTTP requests to the exact IP address discovered in the step above. 

In your Python codebase (where Felix processes the voice commands), update your request URLs like this:

```python
# ⚠️ PASTE YOUR ESP8266 IP ADDRESS HERE
def steruj_swiatlem(akcja):
    ip_esp = "HERE PASTE ESP IP" 
    
    try:
        if akcja == "on":
            requests.get(f"http://{ip_esp}/OFF", timeout=2)
        else:
            requests.get(f"http://{ip_esp}/ON", timeout=2)
    except:
        mow("")
