from .client import *
from .slave import *
from .task import *
from ..task.task import *
from ..task.sleep_task import *

client_session_manager = ClientSessionManager()
slave_manager = SlaveManager()
task_manager = TaskManager()

class ClientMessageHandler(object):

    def __init__(self):
        pass

    def handle_msg(self, msg_header, msg_body):
        session_identity = ClientSessionIdentity("addr")
        msg_name = "__THIS_IS_MSG_NAME__"
        ClientMessageHandler.__handler_dict[msg_name](self, session_identity, msg_body)


    def _h_task_register_req(self, session_identity, msg_body):
        # extract some data from msg_body using protocol.
        result_receiver_address = None # must be specified
        task_token = b"__THIS_IS_TASK_TOKEN__"
        task_type = TaskType.TYPE_SLEEP_TASK
        task = SleepTask(SleepTaskJob(10))

        task_manager.add_task(task)
        session = ClientSession.make_session_from_identity(session_identity, task)
        client_session_manager.add_session(session)

        # send "Task Register Res" using protocol.


    def _h_task_register_ack(self, session_identity, msg_body):
        session = client_session_manager.find_session(session_identity)
        task = session.task
        task_manager.change_task_status(task, TaskStatus.STATUS_WAITING)
        client_session_manager.del_session(session)

        # invoke scheduler


    def _h_task_cancel_req(self, session_identity, msg_body):
        # extract some data from msg_body using protocol.
        task_token = b"__THIS_IS_TASK_TOKEN__"

        task_manager.del_task(task_token)

        # send "Task Cancel Req" using protocol.

    __handler_dict = {
        "Task Register Req" : _h_task_register_req,
        "Task Register Ack" : _h_task_register_ack,
        "Task Cancel Req" : _h_task_cancel_req
    }


class SlaveMessageHandler(object):

    def __init__(self):
        pass

    def handle_msg(self, msg_header, msg_body):
        slave_identity = SlaveIdentity("addr")
        msg_name = "__THIS_IS_MSG_NAME__"
        SlaveMessageHandler.__handler_dict[msg_name](self, slave_identity, msg_body)


    def _h_heart_beat_res(self, msg_body):
        pass


    def _h_slave_register_req(self, msg_body):
        pass


    def _h_task_register_req(self, msg_body):
        pass


    def _h_task_cancel_req(self, msg_body):
        pass


    def _h_task_finish_req(self, msg_body):
        pass


    __handler_dict = {
        "Heart Beat Res" : _h_heart_beat_res,
        "Slave Register Req" : _h_slave_register_req,
        "Task Register Req" : _h_task_register_req,
        "Task Cancel Req" : _h_task_cancel_req,
        "Task Finish Req" : _h_task_finish_req
    }