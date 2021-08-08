import requests
import json
from datetime import date
import time

class Vkontakte:

    def get_id(self):
        name_user = input("Input id(only number) or nickname: ")
        with open("vktoken.txt") as file:
            vktoken = file.read().strip()
        url = "https://api.vk.com/method/utils.resolveScreenName"
        params = {
            "screen_name": {name_user},
            "access_token": vktoken,
            "v": "5.77"
        }
        response2 = requests.get(url=url, params=params)
        check_object_id = response2.json()["response"]
        if name_user.isdigit() == False:
            if "object_id" in check_object_id:
                return response2.json()["response"]["object_id"]
            else:
                print("Wrong username or id, copy photo from our page")
        elif name_user.isdigit() == True:
            return name_user

    def photos_get_vk(self):
        user_id = self.get_id()
        href_dict = dict()
        json_list = []
        self.href_dict = href_dict
        self.json_list = json_list
        with open("vktoken.txt") as file:
            vktoken = file.read().strip()
        url = "https://api.vk.com/method/photos.get"
        params = {
            "user_id": {user_id},
            "access_token": vktoken,
            "v": "5.77",
            "album_id": "profile",
            "extended": "1"
        }

        current_date = date.today()
        response = requests.get(url=url, params=params)
        if "response" in response.json():
            photograph = response.json()["response"]["items"]
            for photo in photograph:
                if photo["likes"]["count"] in href_dict.values():
                    photo["likes"]["count"] = f'{photo["likes"]["count"]}({current_date})'
                href_dict[photo["sizes"][-1]["url"]] = photo["likes"]["count"]
                files_dict = dict()
                files_dict["file_name"] = f'{photo["likes"]["count"]}.jpg'
                files_dict["size"] = photo["sizes"][-1]["type"]
                json_list.append(files_dict)
        else:
            print("Profile closed or deleted")


class Yandexdisk(Vkontakte):

    def get_ya_headers(self):
        with open("yatoken.txt") as file:
            yatoken = file.read().strip()
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(yatoken)
        }

    def upload_by_url(self, file_path, url):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_ya_headers()
        params = {"path": file_path, "url": url, "overwride": "true"}
        response = requests.post(upload_url, headers=headers, params=params)
        if response.status_code == 202:
            print("Response from server - OK")
            return response.json()
        else:
            print("No response from server!")

    def download_json(self, json_length):
        out_file = open('json_out', 'w+')
        json.dump(self.json_list[0:json_length], out_file)

    def crate_folder(self):
        name_folder = input("Input name folder: ")
        self.name_folder = name_folder
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_ya_headers()
        params = {"path": name_folder}
        requests.put(upload_url, headers=headers, params=params)

    def upload_by_dict(self):
        self.photos_get_vk()
        self.crate_folder()
        href_dict = self.href_dict
        quantity_photo = int(input("Input quantity photo(enter = default('5')): ") or "5")
        if len(href_dict) >= quantity_photo:
            print("Begin uploading...")
            dict_by_number = list(enumerate(href_dict.items()))
            for tuple_list in dict_by_number[0:quantity_photo]:
                time.sleep(1)
                self.upload_by_url(f"{self.name_folder}/{tuple_list[1][1]}.jpg", {tuple_list[1][0]})
                print(f"File {tuple_list[1][1]}.jpg upload")
            self.download_json(json_length=quantity_photo)
            print(f"Done, {quantity_photo} file(s) uploaded")
        elif len(href_dict) == 0:
            print("No photo for copy")
        else:
            print(f"Not enough photo in profile, only {len(href_dict)} photo(s) is available")

if __name__ == "__main__":
    vkcopy = Yandexdisk()
    vkcopy.upload_by_dict()