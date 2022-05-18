import datetime
import requests
import json
import config
import uuid
import traceback
from logging import info, error, basicConfig, INFO, ERROR
from datetime import date
import csv
import time


class RevGen:
    def __init__(self) -> None:
        self.headers_post =  {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'accept': 'application/json, text/plain, /',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'x-device-id': config.DEVICE_ID,
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://business.revolut.com/',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={config.REV_TOKEN}',
        }
        
        self.headers_get = {
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'x-device-id': config.DEVICE_ID,
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://business.revolut.com/',
            'accept-language': 'en-US;q=0.9',
            'cookie': f'token={config.REV_TOKEN}',        
        }

        self.s = requests.Session()
        self.business_id = self.get_business()
        if not self.business_id:
            raise RuntimeError("Cannot Get Business API")
        if self.kyc_status != "PASSED":
            raise RuntimeError("Account Unverified")
        
        self.BASE_URL = config.BASE_URL + f"business/{self.business_id}"

        card_ids = self.get_cards()
        for card_id in card_ids:
            self.delete_card(card_id)
                
    @staticmethod
    def log_info(*args, **kwargs):
        
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        st,en = '\033[92m','\033[0m'
        output =  f"{st}[{str(timestamp)}] {args[0]}{en}"
        basicConfig(format="%(message)s", level=INFO)
        info(output)  
        
        
    @staticmethod
    def log_error(*args, **kwargs):
        st,en = '\033[91m','\033[0m'
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        output =  f"{st}[{str(timestamp)}] {args[0]}{en}"
        basicConfig(format="%(message)s", level=ERROR)
        error(output)  
                      
        
    def get_business(self):
        self.log_info("Getting Business")
        
        response = self.s.get(
            config.CURRENT_USER,
            headers=self.headers_get
            )
        
        if "This action is forbidden" in response.text:
            raise RuntimeError("Token Expired")
        
        try:
            parsed = response.json()

            self.kyc_status = parsed["kyc"]
            business_id = parsed["businessId"]
            return business_id
        except:
            self.log_error(f"Error Parsing API: {response.status_code} - {response.text} - {traceback.format_exc()}")
    
    def get_cards(self):
        response = self.s.get(
            f'{self.BASE_URL}/team/members/current-member/cards',
            headers=self.headers_get,
        )
        
        if "This action is forbidden" in response.text:
            raise RuntimeError("Token Expired")

        ids = []
        for card in response.json():
            if card['payload']['virtual']:
                ids.append(card['payload']['id'])

        return ids

    def delete_card(self, card_id):
        response = self.s.post(
            f'{self.BASE_URL}/card/{card_id}/terminate',
            headers=self.headers_post,
        )

        if "This action is forbidden" in response.text:
            raise RuntimeError("Token Expired")

if __name__ == "__main__":
    pass

RevGen()
        
            
                 
        
        
        
            