import zmq, time
#import protocol.master_slave as msp 
import master_slave_pb2 as ms_proto


class HeaderError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        print("HeaderError : %s" % msg)

class msp():
    message_table = {
            'heart_beat': {
                'this': ms_proto.HeartBeat,
            },
            'slave_register': {
                'this': ms_proto.SlaveRegister,
            },
            'task_register' : {
                'this': ms_proto.TaskRegister,
                'result_receiver_address': ms_proto.TaskRegister.ResultReceiverAddress,
                'task': {
                    'sleep_task': ms_proto.TaskRegister.SleepTask,
                    'tensorflow_learning_task': ms_proto.TaskRegister.TensorflowLearningTask,
                    'tensorflow_test_task': ms_proto.TaskRegister.TensorflowTestTask
                }
            }
        }

    @classmethod
    def make_packet(cls, header, body):
        msg_meta = cls.message_table.get(header)

        if msg_meta == None:
            raise HeaderError('%s is not valid header' % header)
        
        for key, val in msg_meta.items():
            if key == 'this':
                msg_type = val
            else:
                if type(val) is dict:
                    if key == 'task':
                        body[body[key + '_type']] = val[body[key + '_type']](**body[key])
                        
                        body.pop(key + '_type')
                        body.pop('task')
                else:
                    body[key] = val(**body[key])


        msg = { header: cls.message_table[header]['this'](**body) }
        return ms_proto.Message(**msg).SerializeToString()

    @classmethod
    def parse_packet(cls, packet):
        packet
    

context = zmq.Context()

req_sock = context.socket(zmq.REQ)

req_url = 'tcp://*:8885'
req_sock.bind(req_url)

heart_beat_body = {}
slave_register_body = {}
task_register_body = { 
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
testset = [
        ('heart_beat', heart_beat_body),
        ('slave_register', slave_register_body), 
        ('task_register', task_register_body),
        ]

packets = list()
for header, body in testset:
    packets.append(msp.make_packet(header, body))

for p in packets:
    req_sock.send(p)
    req_sock.recv()
