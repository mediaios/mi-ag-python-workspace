
from agora.rtc.rtc_connection_observer import IRTCConnectionObserver
class MiConnectionObserver(IRTCConnectionObserver):
    def __init__(self):
        super(MiConnectionObserver,self).__init__()

    def on_connected(self, agora_rtc_conn, conn_info, reason):
        print("QiDebug,MiConnectionObserver,  Connected:", agora_rtc_conn, conn_info.channel_id, conn_info.local_user_id, conn_info.state,
              conn_info.id, conn_info.internal_uid, reason)

    def on_connecting(self, agora_rtc_conn, conn_info, reason):
        print("QiDebug,MiConnectionObserver,  Connecting:", agora_rtc_conn, conn_info, reason)

    def on_disconnected(self, agora_rtc_conn, conn_info, reason):
        print("QiDebug,MiConnectionObserver, Disconnected:", agora_rtc_conn, conn_info, reason)

    def on_user_joined(self, agora_rtc_conn, user_id):
        print("QiDebug,MiConnectionObserver,  on_user_joined:", agora_rtc_conn, user_id)