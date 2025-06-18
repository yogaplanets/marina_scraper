import asyncio
import aiohttp
import csv
from aiohttp import ClientSession
from bs4 import BeautifulSoup

LOGIN_URL = "https://how-to-buy-sailboat.com/api/login"
MARINA_URL_TEMPLATE = "https://how-to-buy-sailboat.com/app/marinas/{id}"
USERNAME = "schepercgs@gmail.com"
PASSWORD = "Cgs261964"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

OUTPUT_FILE = "marinas.csv"

async def login(session):
    payload = {
        "email": USERNAME,
        "password": PASSWORD
    }
    async with session.post(LOGIN_URL, json=payload, headers=HEADERS) as resp:
        if resp.status == 200:
            print("✅ Login successful")
        else:
            print("❌ Login failed")
            raise Exception("Login failed")

async def fetch_marina(session, marina_id):
    url = MARINA_URL_TEMPLATE.format(id=marina_id)
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                return parse_html(marina_id, html)
            else:
                print(f"❌ Failed to fetch {marina_id}: {response.status}")
                return None
    except Exception as e:
        print(f"⚠️ Error on {marina_id}: {e}")
        return None

def parse_html(marina_id, html):
    soup = BeautifulSoup(html, "html.parser")
    try:
        title = soup.select_one("h1").text.strip()
        vhf = soup.select_one("body").text.split("VHF:")[1].split("\n")[0].strip()
        price = soup.select_one("body").text.split("€/día")[0].split()[-1] + " €"
        address = soup.select_one("div:contains('Dirección:')").text.split("Dirección:")[-1].strip()
        return {
            "ID": marina_id,
            "Title": title,
            "VHF": vhf,
            "Price": price,
            "Address": address
        }
    except Exception as e:
        print(f"⚠️ Parse error on {marina_id}: {e}")
        return None

async def main():
    async with ClientSession() as session:
        await login(session)
        tasks = [fetch_marina(session, i) for i in range(1, 10000)]
        results = await asyncio.gather(*tasks)

    # Filter and save
    results = [r for r in results if r]
    keys = results[0].keys() if results else []
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Done. Saved {len(results)} marinas to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
