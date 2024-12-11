import requests


class NotionApi:
    def __init__(self, database_id, headers, proxies=None):
        self.database_id = database_id
        self.headers = headers
        self.proxies = proxies

    def get_pages(self, num_pages=None):
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        get_all = num_pages is None
        page_size = 100 if get_all else num_pages

        payload = {"page_size": page_size}
        response = requests.post(url, json=payload, headers=self.headers, proxies=self.proxies)

        data = response.json()
        results = data["results"]
        while data["has_more"] and get_all:
            payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
            url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
            response = requests.post(url, json=payload, headers=self.headers, proxies=self.proxies)
            data = response.json()
            results.extend(data["results"])

        return data

    def update_page(self, page_id: str, data: dict):
        url = f"https://api.notion.com/v1/pages/{page_id}"

        payload = {"parent": {"database_id": self.database_id}, "properties": data}

        res = requests.patch(url, json=payload, headers=self.headers, proxies=self.proxies)
        return res

    def create_page(self, data: dict):
        create_url = "https://api.notion.com/v1/pages"

        payload = {"parent": {"database_id": self.database_id}, "properties": data}

        res = requests.post(create_url, json=payload, headers=self.headers, proxies=self.proxies)
        print("Status Code:", res.status_code)
        print("Response:", res.json())
        return res

class CommandOperator:
    def __init__(self, notion_token: str, member_database_id: str, log_database_id: str, progress_database_id: str):
        headers = {
            "Authorization": "Bearer " + notion_token,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        proxies = {"http": None, "https": None}
        self.member_database = NotionApi(member_database_id, headers, proxies)
        self.log_database = NotionApi(log_database_id, headers, proxies)
        self.progress_database = NotionApi(progress_database_id, headers, proxies)
        self.member_data = self.member_database.get_pages()["results"]

    def get_entry_by_qq(self, qq_number):
        for entry in self.member_data:
            try:
                if entry['properties']['qq号']['rich_text'] and \
                        entry['properties']['qq号']['rich_text'][0]['text']['content'] == qq_number:
                    return entry  # 返回找到的整条记录
            except (KeyError, IndexError, TypeError) as e:
                # 捕获可能的键错误或索引错误，跳过这个条目
                print(f"Skipping entry due to error: {e}")
                continue
        return None  # 如果没有找到对应的QQ号

    def get_entry_by_member_openid(self, member_openid):
        for entry in self.member_data:
            try:
                if entry['properties']['member_openid']['rich_text'] and \
                        entry['properties']['member_openid']['rich_text'][0]['text']['content'] == member_openid:
                    return entry
            except (KeyError, IndexError, TypeError) as e:
                # 捕获可能的键错误或索引错误，跳过这个条目
                print(f"Skipping entry due to error: {e}")
                continue
        return None  # 如果没有找到对应的QQ号

    def init_qq_id_pair(self, qq_number, member_openid):
        try:
            entry = self.get_entry_by_qq(qq_number)
        except (KeyError, IndexError, TypeError) as e:
            # 捕获可能的键错误或索引错误，跳过这个条目
            print(f"Skipping entry due to error: {e}")
            return
        data = {
            "member_openid": {'type': 'rich_text',
                              'rich_text': [{'type': 'text', 'text': {'content': member_openid}}]},
        }
        res = self.member_database.update_page(entry["id"], data)
        print(f"Init command: {qq_number}")
        return res

    def create_notion_log(self, log_content: str, user_id=None, group_name=None):
        data = {
            "日志内容": {"title": [{"text": {"content": log_content}}]},
            'Status': {'type': 'status', 'status': {'name': '已记录'}},
            "关联人员": {'type': 'people', "people": [{"id": user_id}]},
            "关联组": {'type': 'multi_select', 'multi_select': [{'name': group_name}]},
        }
        res = self.log_database.create_page(data)
        return res

    def create_notion_progress(self, progress_content: str, user_id=None, group_name=None):
        data = {
            "进度内容": {"title": [{"text": {"content": progress_content}}]},
            "关联人员": {'type': 'people', "people": [{"id": user_id}]},
            "关联组": {'type': 'multi_select', 'multi_select': [{'name': group_name}]},
        }
        res = self.progress_database.create_page(data)
        return res


def main():
    ...


if __name__ == '__main__':
    main()