import requests

class bot:
    
    def __init__(self, token):
        self.url = 'https://api.telegram.org/bot' + token

    def send_get(self, chat_id, text):
        try:
            response = requests.get(self.url  + '/sendMessage?' + f"text={text}&chat_id={chat_id}&parse_mode=MarkdownV2")
            message_id=response.json()['result']['message_id']
            response.close()
            return message_id
        except:
            return False

    #This method is not used bercause of issues with unicode. GET approach is used instead
    def send_post(self, chat_id, text):
        data = {'chat_id': chat_id, 'text': text}
        try:
            headers = {'content-type': 'application/json; charset=utf-8', 'accept': 'text/plain', }
            response = requests.post(self.url + '/sendMessage', json=data, headers=headers)
            message_id=response.json()['result']['message_id']
            response.close()
            return message_id
        except:
            return False

    #For future implementations
    def deleteMessage(self, chat_id, message_id):
        try:
            response = requests.get(self.url  + '/deleteMessage?' + f"chat_id={chat_id}&message_id={message_id}")
            response.close()
            return True
        except:
            return False

