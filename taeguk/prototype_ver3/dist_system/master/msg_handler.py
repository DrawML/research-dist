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
        result_receiver_address = None  # must be specified
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

        task_manager.cancel_task(task_token)

        # send "Task Cancel Res" using protocol.

    __handler_dict = {
        "Task Register Req": _h_task_register_req,
        "Task Register Ack": _h_task_register_ack,
        "Task Cancel Req": _h_task_cancel_req
    }


class SlaveMessageHandler(object):
    def __init__(self):
        pass

    def handle_msg(self, msg_header, msg_body):
        slave_identity = SlaveIdentity("addr")
        msg_name = "__THIS_IS_MSG_NAME__"
        SlaveMessageHandler.__handler_dict[msg_name](self, slave_identity, msg_body)

    def _h_heart_beat_res(self, slave_identity, msg_body):
        slave_manager.find_slave(slave_identity).heartbeat()

    def _h_slave_register_req(self, slave_identity, msg_body):
        slave_manager.add_slave(Slave.make_slave_from_identity(slave_identity))

        # send "Slave Register Res" using protocol.

    def _h_task_register_res(self, slave_identity, msg_body):
        slave = slave_manager.find_slave(slave_identity)

        # extract some data from msg_body using protocol.
        task_token = b"__THIS_IS_TASK_TOKEN__"
        status = 'success'
        error_code = None

        if status == 'success':
            # check if task's status == TaskStatus.STATUS_WAITING
            # or(and)
            # check task register req가 갔었는지 올바른 res인지 check가 필요.
            # 여기부분외에도 여러부분에서 이런 처리가 필요할 것이다.
            # 그러나 일단 이부분은 후순위로 두고 일단 빠른 구현을 목표로 한다.
            # 추후에 구현완료 후 보완하도록 하자.
            task_manager.change_task_status(task_token, TaskStatus.STATUS_PROCESSING)
        elif status == 'fail':
            task = task_manager.find_task(task_token)
            slave.delete_task(task)
            task_manager.redo_leak_task(task)
        else:
            pass


    def _h_task_cancel_res(self, slave_identity, msg_body):
        # 뭘 해야하지... 흠.. 그냥 프로토콜에서 뺄까?
        pass

    def _h_task_finish_req(self, slave_identity, msg_body):
        slave = slave_manager.find_slave(slave_identity)

        # extract some data from msg_body using protocol.
        task_token = b"__THIS_IS_TASK_TOKEN__"

        task = task_manager.find_task(task_token)
        slave.delete_task(task)
        task_manager.change_task_status(task, TaskStatus.STATUS_COMPLETE)

        # send "Task Finish Res" using protocol. 근데 이거 굳히 필요한가..? 흠..

    __handler_dict = {
        "Heart Beat Res": _h_heart_beat_res,
        "Slave Register Req": _h_slave_register_req,
        "Task Register Res": _h_task_register_res,
        "Task Cancel Res": _h_task_cancel_res,
        "Task Finish Req": _h_task_finish_req
    }
