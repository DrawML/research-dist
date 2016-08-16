import zmq, time
from protocol import master_slave as msp 

context = zmq.Context()

req_sock = context.socket(zmq.REQ)

req_url = 'tcp://*:8885'
req_sock.bind(req_url)

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

testset = [
        ('heart_beat_req', heart_beat_req_body),
        ('slave_register_req', slave_register_req_body), 
        ('task_register_req', task_register_req_body),
        ('task_cancel_req', task_cancel_req_body),
        ('task_finish_req', task_finish_req_body),
        ]

packets = list()
for header, body in testset:
    packets.append(msp.make_packet(header, body))
    print("<Header: %s>\n%s" % (header, body))

for p in packets:
    req_sock.send(p)
    recv_packet = req_sock.recv()

    header, body = msp.parse_packet(recv_packet)
    print("<Header: %s>\n%s" % (header, body))

