import io
import time
import base64
import json
import csv
import os
import random
import re
from PIL import Image
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail SMTP server configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Configure Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280,1080")  # Set an initial window size
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")



# SETUP
client = OpenAI()
_ = load_dotenv()
# Initialize the web driver (make sure you have ChromeDriver installed and in PATH)
driver = webdriver.Chrome(options=chrome_options)

PRODUCT_TO_TRACK="iphone 15 pro max"
FILE_NAME="iphone_15_pro_max_history.csv"
STORES_URLS=["https://www.aquario.pt/pt/product/apple-smartphone-apple-iphone-15-pro-max-256gb-tita-pret-mu773ql-a",
             "https://www.aquario.pt/pt/product/apple-smartphone-apple-iphone-15-pro-max-256gb-tita-azul-mu7a3ql-a",
             "https://www.aquario.pt/pt/product/apple-smartphone-apple-iphone-15-pro-max-256gb-tita-bran-mu783ql-a",
             "https://www.radiopopular.pt/produto/apple-iphone-15-pro-max-256gb-bl",
             "https://www.radiopopular.pt/produto/apple-iphone-15-pro-max-256gb-bk",
             "https://www.castroelectronica.pt/product/iphone-15-pro-max-67-256gb-titanio-azul--apple?utm_source=kuantokusta&utm_medium=cpc&utm_campaign=catalogo",
             "https://www.castroelectronica.pt/product/iphone-15-pro-max-67-256gb-titanio-natural--apple",
             "https://www.castroelectronica.pt/product/iphone-15-pro-max-67-256gb-titanio-branco--apple",
             "https://www.amazon.es/-/pt/dp/B0CHWZ6YV6/ref=sr_1_4?crid=ODC1FRN2RR4U&dib=eyJ2IjoiMSJ9.1sQfVS1roxkXNHHLiB54jHw_XjAwwZKqmh5ZTARVntJwj4QErzaB6hu0wVOVSexYIbPGaId7HnfV_kjYUwDCP9vC6rVx0R3Ra-q-YnPOkSw2zqbeyGf7znk3YLOWEKmkPGEExNaWDBidUp0w3jXk3jqRCDvEtv0s-ZblPdO_eKqLzAngJgr1jVhVo6b9ogNMWlonczP1eeZeZC_3yYjTtQuptbgEBpaD3IVUVpFZ9mRANsrDJvdEgGDdVYj3_ce5AA1cKjSN6ivZWGCNlWXjRe7f_-EtNVl49Hv6iurcXhQ.5Nth6xJ1zZAafEIs3vnUg2oG8BCZfZ0KpdE35RwhBKI&dib_tag=se&keywords=iphone%2B15%2Bpro%2Bmax%2B256gb&nsdOptOutParam=true&qid=1732215714&sprefix=iphone%2B15%2Bpro%2Bmax%2Caps%2C345&sr=8-4&th=1",
             "https://www.kuantokusta.pt/p/10379596/apple-iphone-15-pro-max-67-256gb-blue-titanium",
             "https://www.kuantokusta.pt/p/10379598/apple-iphone-15-pro-max-67-256gb-natural-titanium",
             "https://www.kuantokusta.pt/p/10379599/apple-iphone-15-pro-max-67-256gb-black-titanium",
             "https://www.kuantokusta.pt/p/10379597/apple-iphone-15-pro-max-67-256gb-white-titanium",
             "https://chipman.pt/smartphones-iphone/telem%C3%B3vel-apple-iphone-15-pro-max-67-256gb-tit%C3%A2nio-azul-mu7a3qla",
             "https://www.istore.pt/apple-iphone-15-pro-max-256gb-ti-branco",
             "https://www.istore.pt/apple-iphone-15-pro-max-256gb-ti-natural",
             "https://www.istore.pt/apple-iphone-15-pro-max-256gb-ti-preto",
             "https://www.istore.pt/apple-iphone-15-pro-max-256gb-ti-azul"


    ]

# TEST_STORES=[STORES_URLS[random.randint(0,len(STORES_URLS)-1)]]

# TEST_STORES=["https://www.radiopopular.pt/produto/tablet-samsung-tab-a9-128gb-grey"]

SYSTEM_MSG="""You are product comparison expert and you will analyse the price of a product. 
You will be given an image of a website, and output: 1) the name of the item, 2) the current price with the appropriate currency, 4) any relevant notes such as ongoing deals and 5) the name of the store. 
You will return this information in JSON format and add any relevant fields for any other defining features such as color. Think step by step to solve this problem."""

def compress_image(base64_image):
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))

    # Convert and compress to JPEG
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=60)  # Adjust quality
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def get_screenshot_from_url(url):
    driver.get(url)
    # Wait for a specific element to load (e.g., body)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    

    # total_height = driver.execute_script("return document.body.scrollHeight")
    # driver.set_window_size(1920, total_height)  # Adjust window to the full page height
    time.sleep(3)
    # Take a screenshot of body and get it as Base64
    element = driver.find_element(By.TAG_NAME, "body")
    base64_image = element.screenshot_as_base64
    compressed_image = compress_image(base64_image)
    # base64_image = driver.get_screenshot_as_base64()
    save_png(compressed_image)
    return compressed_image

def save_png(base64_image, filename="output" ):
    # Optional: Save as a file locally for verification
    with open(f"{filename}.png", "wb") as f:
         f.write(base64.b64decode(base64_image))


def get_ai_image_analysis(base64_image):
    # AI IMAGE ANALYSIS
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", 
             "content": [
                 {
                "type": "text",
                "text": f"Find me info about {PRODUCT_TO_TRACK}",
                },
                {
                "type": "image_url",
                "image_url": {
                    "url":  f"data:image/jpeg;base64,{base64_image}"
                },
                },
             ]
            }
        ],
        response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "product_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "description": "The name of the product",
                        "type": "string"
                    },
                    "price": {
                    "description": "The cost of the product",
                    "type": "string"
                    },
                    "notes": {
                    "description": "Any other relevant information such as stock, deals and promotions",
                    "type": "string"
                    },
                     "store": {
                    "description": "The name of the store that is selling the product",
                    "type": "string"
                    },
                    "additionalProperties": True
                }
            }
        }
    }
    )
    return completion.choices[0].message.content

def save_info_to_csv(price_results:Dict, csv_file="output.csv"):
    """
    Writes or appends data from a list of dictionaries to a CSV file.
    Adds a 'timestamp' column as the first or last column in the CSV.
    - If the file exists, appends the new data.
    - If the file doesn't exist, creates it and writes the data.
    """
    file_exists = os.path.exists(csv_file)
    
    # Add the timestamp column dynamically
    fieldnames = list(price_results[0].keys()) + ["timestamp"]  # Timestamp at the end

    with open(csv_file, mode="a" if file_exists else "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header only if the file doesn't exist
        if not file_exists:
            writer.writeheader()
        
        # Add a timestamp to each row (not modifying the original data)
        for row in price_results:
            row_with_timestamp = {**row, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            writer.writerow(row_with_timestamp)

        if file_exists:
            print(f"Data appended to '{csv_file}'.")
        else:
            print(f"File '{csv_file}' created and data written.")

sys_msg1=f"""You are product comparison expert and you will analyse the cheapeast 
option out of a collection of data about different stores and options selling {PRODUCT_TO_TRACK}.
Remember you can do maths if needed and make sure to compare all prices before responding. Think step by step.
"""

def analyse_batch_results(json_results):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": sys_msg1},
            {"role": "user", 
             "content": [
                 {
                "type": "text",
                "text": f"""Today is What is {datetime.now().strftime("%Y-%m-%d %H:%M")} with formatting %Y-%m-%d %H:%M. 
                What is the bests {PRODUCT_TO_TRACK} to purchase? Do an analysis and think step by step to answer the questions.
                ```{json_results}```
                Format your answer in XML tags:
                - <thinking> tag Do your thinking inside <thinking>. The customer will not see this.
                - <body> Write plain text in body of the email to the client. Make sure to include relevant details of the deal and product chosen, including color, price store, url etc as well as a summary analysis on why it's best than other options. If there are multiple options with the better price, include all. Briefly compare the best deal with the second best deal.
                - <subject> Write an email subject and make sure it contains the cheapest price you found.
                """,
                },
             ]
            }
        ],)
    return completion.choices[0].message.content


def format_table_from_list(data: List[Dict]) -> str:

    if not data:
        return "No data to display."

    # Dynamically generate headers from keys of the first dictionary
    headers = data[0].keys()
    header_row = " | ".join(f"{header.capitalize():<12}" for header in headers)
    separator = "-" * len(header_row)

    # Generate rows dynamically
    rows = [
        " | ".join(f"{str(item[key]):<12}" for key in headers)
        for item in data
    ]

    # Combine header, separator, and rows into the final string
    formatted_string = f"{header_row}\n{separator}\n" + "\n".join(rows)
    return formatted_string

def send_email(subject, body):

    # Gmail login credentials
    email = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASS")
    receiver_email = os.environ.get("RECEIVER_EMAIL")


    # Create the email
    message = MIMEMultipart()
    message["From"] = email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Connect to Gmail's SMTP server and send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(email, password)  # Login to your Gmail account
            server.sendmail(email, receiver_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

def main():
    price_results=[]
    try: 
        for url in STORES_URLS:
            base64_image = get_screenshot_from_url(url)
            json_output = get_ai_image_analysis(base64_image)
            dict_result = json.loads(json_output)
            dict_result["url"] = url
            price_results.append(dict_result)
        save_info_to_csv(price_results)
        json_results = json.dumps(price_results, indent=4)
        xml_email_content = analyse_batch_results(json_results)
        results_table = format_table_from_list(price_results)
        
        # Extract thinking using regex
        thinking_match = re.search(r"<thinking>(.*?)</thinking>", xml_email_content, re.DOTALL)
        thinking = thinking_match.group(1).strip() if thinking_match else "No thinking found"
        # TODO: log thinking

        # Extract subject using regex
        subject_match = re.search(r"<subject>(.*?)</subject>", xml_email_content, re.DOTALL)
        subject = subject_match.group(1).strip() if subject_match else "No subject found"

        # Extract body using regex
        body_match = re.search(r"<body>(.*?)</body>", xml_email_content, re.DOTALL)
        body = body_match.group(1).strip() if body_match else "No body found"
    
        print(xml_email_content)
        send_email(subject, body+results_table)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
    