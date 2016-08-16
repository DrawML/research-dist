from .proto import master_slave_pb2 as ms_proto
from .exceptions import HeaderError

message_table = {
        'heart_beat_req': {
            'this': ms_proto.HeartBeatRequest,
        },
        'heart_beat_res': {
            'this': ms_proto.HeartBeatResponse,
        },
        'slave_register_req': {
            'this': ms_proto.SlaveRegisterRequest,
        },
        'slave_register_res': {
            'this': ms_proto.SlaveRegisterResponse,
        },
        'task_register_req' : {
            'this': ms_proto.TaskRegisterRequest,
            'result_receiver_address': ms_proto.TaskRegisterRequest.ResultReceiverAddress,
            'task': {
                'sleep_task': ms_proto.TaskRegisterRequest.SleepTask,
                'tensorflow_learning_task': ms_proto.TaskRegisterRequest.TensorflowLearningTask,
                'tensorflow_test_task': ms_proto.TaskRegisterRequest.TensorflowTestTask
            }
        },
        'task_register_res' : {
            'this': ms_proto.TaskRegisterResponse,
        },
        'task_cancel_req' : {
            'this': ms_proto.TaskCancelRequest,
        },
        'task_cancel_res' : {
            'this': ms_proto.TaskCancelResponse,
        },
        'task_finish_req' : {
            'this': ms_proto.TaskFinishRequest,
        },
        'task_finish_res' : {
            'this': ms_proto.TaskFinishResponse,
        },
    }

def handle_extra(data, key):
    if key == 'task':
        data[data[key + '_type']] = val[data[key + '_type']](**data[key])

        data.pop(key + '_type')
        data.pop(key)
    else:
        raise



def make_packet(header, body):
    import copy
    data = copy.deepcopy(body) 

    msg_meta = message_table.get(header)

    if msg_meta == None:
        raise HeaderError('%s is not valid header' % header)
    
    for key, val in msg_meta.items():
        if key == 'this':
            msg_type = val
        else:
            if type(val) is dict:
                handle_extra(data, key)
            else:
                data[key] = val(**data[key])


    msg = { header: message_table[header]['this'](**data) }
    return ms_proto.Message(**msg).SerializeToString()

def parse_packet(packet):
    msg = ms_proto.Message()
    msg.ParseFromString(packet)
    return msg.WhichOneof('body'), msg
