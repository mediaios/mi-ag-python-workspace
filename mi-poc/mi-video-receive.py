from operator import truediv

from agora.rtc.agora_base import *


import time
import  os
from observer.path_utils import get_log_path_with_filename
from observer.mi_connection_observer import MiConnectionObserver
from observer.mi_audio_frame_observer import MiAudioFrameObserver
from observer.mi_local_user_observer import MiLocalUserObserver
from observer.mi_video_frame_observer import MiVideoFrameObserver
from agora.rtc.agora_service import AgoraServiceConfig, AgoraService
from observer.mi_zhipu_video_frame_observer import MiZhiPuVideoFrameObserver

from agora.rtc.local_user_observer import IRTCLocalUserObserver
from agora.rtc.rtc_connection import RTCConnConfig
config = AgoraServiceConfig()
config.appid = "20338919f2ca4af4b1d7ec23d8870b56"
config.audio_scenario = AudioScenarioType.AUDIO_SCENARIO_CHORUS
agora_engine = AgoraService()
config.enable_video = 1
config.log_path = get_log_path_with_filename(os.path.splitext(__file__)[0])
print("qidebug, log path",config.log_path)
agora_engine.initialize(config)

def create_conn(channel_id,uid=0):
    con_config = RTCConnConfig(
        auto_subscribe_audio = 1,
        auto_subscribe_video = 1,
        client_role_type = ClientRoleType.CLIENT_ROLE_BROADCASTER,
        channel_profile = ChannelProfileType.CHANNEL_PROFILE_LIVE_BROADCASTING,
    )


    connection = agora_engine.create_rtc_connection(con_config)

    conn_observer = MiConnectionObserver()
    connection.register_observer(conn_observer)
    connection.connect("",channel_id,str(uid))

    #local user config
    local_user = connection.get_local_user()
    local_user.set_playback_audio_frame_before_mixing_parameters(1,16000)
    local_user_observer = MiLocalUserObserver()
    local_user.register_local_user_observer(local_user_observer)

    #register audio frame callback
    # audio_frame_observer = MiAudioFrameObserver()
    # local_user.register_audio_frame_observer(audio_frame_observer)
    # local_user.subscribe_all_audio()

    #register video frame callback
    media_node_factory = agora_engine.create_media_node_factory()
    video_sender = media_node_factory.create_video_frame_sender()
    video_track = agora_engine.create_custom_video_track_frame(video_sender)
    video_frame_observer = MiVideoFrameObserver()
    local_user.register_video_frame_observer(video_frame_observer)
    # video_frame_observer = MiZhiPuVideoFrameObserver()
    # local_user.register_video_frame_observer(video_frame_observer)
    video_track.set_enabled(1)
    # local_user.subscribe_all_video()


    time.sleep(100)
    # local_user.unpublish_audio(audio_track)
    # audio_track.set_enabled(0)
    video_track.set_enabled(0)
    connection.unregister_observer()
    connection.disconnect()
    connection.release()
    print("release")


create_conn("qitest",9999999)

agora_engine.release()
print("QiDebug, end")
