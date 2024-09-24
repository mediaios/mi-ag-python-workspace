from agora.rtc.local_user_observer import IRTCLocalUserObserver
class MiLocalUserObserver(IRTCLocalUserObserver):
    def __init__(self):
        super(MiLocalUserObserver, self).__init__()

    def on_stream_message(self, local_user, user_id, stream_id, data, length):
        print("QiDebug,MiLocalUserObserver, on_stream_message:", user_id, stream_id, data, length)
        return 0

    def on_user_info_updated(self, local_user, user_id, msg, val):
        print("QiDebug,MiLocalUserObserver, on_user_info_updated:", user_id, msg, val)
        return 0
