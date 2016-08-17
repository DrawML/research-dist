import zmq, time
from protocol import master_slave as msp 
from protocol import client_master as clmp 
from protocol import slave_worker as swp 
from protocol import any_result_receiver as arrp 

context = zmq.Context()

req_sock = context.socket(zmq.REQ)

req_url = 'tcp://*:8885'
req_sock.bind(req_url)

def get_test(what):
    if what == "master_slave":
        heart_beat_req_body = {}
        slave_register_req_body = {}
        task_register_req_body = { 
                'result_receiver_address': {
                    'type': 'TCP',
                    'ip': '210.118.4.3',
                    'port': 35356
                },
                'task_token': b'892357',
                'task_type': 'sleep_task',
                'task': {
                    'seconds': 300
                }
            }
        task_cancel_req_body = {
                'task_token': b'792358'
                }
        task_finish_req_body = {
                'task_token': b'792358'
                }

        protocol = msp
        testset = [
                ('heart_beat_req', heart_beat_req_body),
                ('slave_register_req', slave_register_req_body), 
                ('task_register_req', task_register_req_body),
                ('task_cancel_req', task_cancel_req_body),
                ('task_finish_req', task_finish_req_body),
                ]
    elif what == "client_master":
        task_register_req_body = { 
                'result_receiver_address': {
                    'type': 'TCP',
                    'ip': '210.118.4.3',
                    'port': 35356
                },
                'task_type': 'sleep_task',
                'task': {
                    'seconds': 300
                }
            }
        task_register_ack_body = {}
        task_cancel_req_body = {
                'task_token': b'792358'
                }

        protocol = clmp
        testset = [
                ('task_register_req', task_register_req_body),
                ('task_register_ack', task_register_ack_body),
                ('task_cancel_req', task_cancel_req_body),
                ]
    elif what == "slave_worker":
        worker_register_req_body = { 
                'task_token': b'792358'
                }
        task_cancel_req_body = {
                'task_token': b'792358'
                }
        task_finish_req_body = {
                'task_token': b'792358'
                }

        protocol = swp 
        testset = [
                ('worker_register_req', worker_register_req_body),
                ('task_cancel_req', task_cancel_req_body),
                ('task_finish_req', task_finish_req_body),
                ]
    elif what == "any_result_receiver":
        task_result_req_body = { 
                'task_token': b'892357',
                'status': 'cancel',
                'error_code': 'unknown',
                'result_type': 'sleep_task',
                'result': {
                    'comment': 'Test'
                }
            }

        protocol = arrp 
        testset = [
                ('task_result_req', task_result_req_body),
                ]

    return protocol, testset

# set test protocol
what = "any_result_receiver"
protocol, testset = get_test(what)

packets = list()
for header, body in testset:
    packets.append(protocol.make_packet(header, body))
    print("<Header: %s>\n%s" % (header, body))

print("[", what, "] Protocol Test Start")
for p in packets:
    req_sock.send(p)
    recv_packet = req_sock.recv()

    header, body = protocol.parse_packet(recv_packet)
    print("<Header: %s>\n%s" % (header, body))

