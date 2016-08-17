import zmq
from protocol import master_slave as msp
from protocol import client_master as clmp 
from protocol import slave_worker as swp 
from protocol import any_result_receiver as arrp 

context = zmq.Context()

rep_url = 'tcp://localhost:8885'

rep_sock = context.socket(zmq.REP)
rep_sock.connect(rep_url)

def get_test(what):
    if what == "master_slave":
        heart_beat_res_body = {}
        slave_register_res_body = {
                'status': 'success',
                }
        task_register_res_body = {
                'status': 'fail',
                'error_code': 'unknown',
                }
        task_cancel_res_body = {
                'status': 'fail',
                'error_code': 'invalid_token',
                }
        task_finish_res_body = {
                'status': 'success',
                }

        protocol = msp
        response_table = {
                'heart_beat_req': ('heart_beat_res', heart_beat_res_body),
                'slave_register_req': ('slave_register_res', slave_register_res_body), 
                'task_register_req': ('task_register_res', task_register_res_body),
                'task_cancel_req': ('task_cancel_res', task_cancel_res_body),
                'task_finish_req': ('task_finish_res', task_finish_res_body),
                }
    elif what == "client_master":
        task_register_res_body = {
                'status': 'fail',
                'task_token': b'12897',
                'error_code': 'unknown',
                }
        task_cancel_res_body = {
                'status': 'fail',
                'error_code': 'busy',
                }
        dummy_body = {}

        protocol = clmp
        response_table = {
                'task_register_req': ('task_register_res', task_register_res_body),
                'task_register_ack': ('task_register_res', dummy_body),
                'task_cancel_req': ('task_cancel_res', task_cancel_res_body),
                }
    elif what == "slave_worker":
        worker_register_res_body = {
                'status': 'fail',
                'error_code': 'unknown',
                }
        task_cancel_res_body = {
                'status': 'fail',
                'error_code': 'unknown',
                }
        task_finish_res_body = {
                'status': 'success',
                }

        protocol = swp
        response_table = {
                'worker_register_req': ('worker_register_res', worker_register_res_body),
                'task_cancel_req': ('task_cancel_res', task_cancel_res_body),
                'task_finish_req': ('task_finish_res', task_finish_res_body),
                }
    elif what == "any_result_receiver":
        task_result_res_body = {
                'status': 'fail',
                'error_code': 'unknown',
                }

        protocol = arrp
        response_table = {
                'task_result_req': ('task_result_res', task_result_res_body),
                }

    return protocol, response_table

what = "any_result_receiver"
protocol, response_table = get_test(what)

print("[", what, "] Protocol Test Start")
while True:
    recv_packet = rep_sock.recv()

    header, body = protocol.parse_packet(recv_packet)
    print("<Header: %s>\n%s" % (header, body))

    res_header, res_body = response_table[header]
    packet = protocol.make_packet(res_header, res_body)
    rep_sock.send(packet)
