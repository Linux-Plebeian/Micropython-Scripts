import network
import urequests
import ujson
import time

# ==== Wi-Fi credentials ====
WIFI_SSID = "Mesh work"
WIFI_PASSWORD = "opensesame1"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Connected:", wlan.ifconfig())

def track_ip(ip):
    url = f"http://ip-api.com/json/{ip}"
    try:
        response = urequests.get(url)
        data = ujson.loads(response.text)
        response.close()

        if data["status"] == "success":
            print(f"IP: {data['query']}")
            print(f"Country: {data['country']}")
            print(f"Region: {data['regionName']}")
            print(f"City: {data['city']}")
            print(f"ZIP: {data['zip']}")
            print(f"Latitude: {data['lat']}")
            print(f"Longitude: {data['lon']}")
            print(f"ISP: {data['isp']}")
        else:
            print("Error:", data.get("message", "Unknown error"))
    except Exception as e:
        print("Request failed:", e)

# ==== Main ====
connect_wifi()
ip_address = input("Enter IP address: ")
track_ip(ip_address)
