from dist_system.slave import slave
from multiprocessing import Process

MASTER_ADDR = 'tcp://127.0.0.1:6000'
WORKER_ROUTER_ADDR = 'tcp://*:700'
SLAVE_ADDR = 'tcp://127.0.0.1:700'
CONTROL_ROUTER_ADDR = 'tcp://*:300'


def _slave_main(idx):
    print("[*] Generate SLAVE #", idx)
    slave.main(MASTER_ADDR, WORKER_ROUTER_ADDR + str(idx), SLAVE_ADDR + str(idx),
               CONTROL_ROUTER_ADDR + str(idx))


NUM_SLAVES = 6

if __name__ == '__main__':
    for idx in range(NUM_SLAVES):

        Process(target=_slave_main, args=(idx,)).start()