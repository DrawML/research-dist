import zmq
from protocol import master_slave as msp

context = zmq.Context()

rep_url = 'tcp://localhost:8885'

rep_sock = context.socket(zmq.REP)
rep_sock.connect(rep_url)

heart_beat_res_body = {}
slave_register_res_body = {
        'status': 'SUCCESS',
        }
task_register_res_body = {
        'status': 'FAIL',
        'error_code': 'UNKNOWN',
        }
task_cancel_res_body = {
        'status': 'FAIL',
        'error_code': 'INVALID_TOKEN',
        }
task_finish_res_body = {
        'status': 'SUCCESS',
        }

response_table = {
        'heart_beat_req': ('heart_beat_res', heart_beat_res_body),
        'slave_register_req': ('slave_register_res', slave_register_res_body), 
        'task_register_req': ('task_register_res', task_register_res_body),
        'task_cancel_req': ('task_cancel_res', task_cancel_res_body),
        'task_finish_req': ('task_finish_res', task_finish_res_body),
        }

while True:
    recv_packet = rep_sock.recv()

    header, body = msp.parse_packet(recv_packet)
    print("<Header: %s>\n%s" % (header, body))

    res_header, res_body = response_table[header]
    packet = msp.make_packet(res_header, res_body)
    rep_sock.send(packet)
