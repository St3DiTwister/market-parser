import vk_api
import random


def send_message(items):
    vk = vk_api.VkApi(token='TOKEN')
    myId = 'ID'
    item = '<br>'.join([str(i) for i in items])
    vk.method("messages.send", {"peer_id": myId, "message": item, "random_id": random.randint(1, 2147483647)})

    return 1