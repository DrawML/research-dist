from dist_system.client import client
from multiprocessing import Process

NUM_CLIENTS = 10


def _client_main(idx):
    print("[*] Generate CLIENT #", idx)
    client.main()

if __name__ == '__main__':
    for idx in range(NUM_CLIENTS):
        Process(target=_client_main, args=(idx,)).start()