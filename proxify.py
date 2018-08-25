import os
import re
import json

from util import *
from localization import get_localized_string, print_localized

class Proxify:

    def __init__(self):
        self.proxies = {
            "https": "http",
            "http://imgur.com": "http://filmot.org",
            "http://i.imgur.com": "http://i.filmot.org",
            "http://pastebin.com": "http://pastebin.seyahdoo.com",
            "http://cubeupload.com": "http://cubeupload.seyahdoo.com",
            "http://u.cubeupload.com": "http://u.cubeupload.seyahdoo.com"
        }

        self.proxy_history = {}
        self.non_special_proxy_history = {}
        self.url_expression = re.compile(
            '(\"https?://((imgur\.com)|(i\.imgur\.com)|(pastebin\.com)|(cubeupload\.com)|(u\.cubeupload\.com))[^\s"]*\")')


    def calculate_proxy(self, original):
        if "/" not in original:
            if original in self.non_special_proxy_history:
                return self.non_special_proxy_history[original]
            return
        else:
            if original in self.proxy_history:
                return self.proxy_history[original]
            pass

        proxy = original
        for o, p in self.proxies.items():
            if proxy.startswith(o):
                proxy = proxy.replace(o, p, 1)

        if proxy is original:
            print("this is not proxified, some kind of error must be happening.")
            print(proxy)
            return

        print(get_localized_string("adding_new_proxy") + " -> " + original + ":" + proxy)
        self.proxy_history[original] = proxy
        self.non_special_proxy_history[get_non_specialized_string(original)] = get_non_specialized_string(proxy)

        return proxy

    def get_proxy_from_original_non_special(self, string):
        if string in self.non_special_proxy_history:
            return self.non_special_proxy_history[string]
        return

    def get_original_from_proxy_non_special(self, string):
        for original, proxy in self.non_special_proxy_history:
            if proxy is string:
                return original
        return

    def is_proxy_or_original(self, string):
        # detect if a file is proxified, original or unrelated
        if "/" in string:
            if string in self.proxy_history.keys():
                return "original"
            elif string in self.proxy_history.values():
                return "proxy"
            return "irrelevant"
        else:
            if string in self.non_special_proxy_history.keys():
                return "original"
            elif string in self.non_special_proxy_history.values():
                return "proxy"
            return "irrelevant"

    def proxify_mod_files_in_folder(self, folder_path):

        # Replace blocked links with proxy links inside json files
        # (without changing modify time so it wont change the order of mods inside game)
        json_files = [pos_json for pos_json in os.listdir(folder_path) if pos_json.endswith('.json')]
        for file_name in json_files:
            file_path = folder_path + file_name
            original_modify_time = os.path.getmtime(file_path)  # capture modify time
            self.proxify_file(file_path)
            os.utime(file_path, (original_modify_time, original_modify_time))  # restore modify time

        # recursively proxify sub folders
        sub_folders = [f.path for f in os.scandir(folder_path) if f.is_dir()]
        for sub_folder in sub_folders:
            self.proxify_mod_files_in_folder(sub_folder + "\\")

        return

    def proxify_file(self, file_path):
        s = None

        with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
            s = f.read()

        proxiable_list = self.url_expression.findall(s)
        if len(proxiable_list) > 0:
            for r in proxiable_list:
                sliced = r[0][1:-1]
                self.calculate_proxy(sliced)
        else:
            return

        for original, proxy in self.proxy_history.items():
            s = s.replace(original, proxy)

        with open(file_path, 'w', encoding='utf8') as f:
            f.write(s)
        return

    def save_proxy_history(self, file_path):
        print(get_localized_string("saving_proxy_history") + file_path)
        s = json.dumps(
            {
                "proxy_history": self.proxy_history,
                "non_special_proxy_history": self.non_special_proxy_history}
            ,indent=4, separators=(',', ': '))

        with open(file_path, 'w', encoding='utf8') as f:
            f.write(s)

        return

    def load_proxy_history(self, file_path):
        print(get_localized_string("loading_proxy_history") + file_path)
        s = None
        with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
            s = f.read()
        j = json.loads(s)
        self.proxy_history = j["proxy_history"]
        self.non_special_proxy_history = j["non_special_proxy_history"]
        return