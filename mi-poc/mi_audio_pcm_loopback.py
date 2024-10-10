from agora.rtc.agora_base import *


import time
import  os
import logging
import asyncio
import signal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from observer.path_utils import get_log_path_with_filename
from agora.rtc.agora_service import AgoraServiceConfig, AgoraService
from agora.rtc.audio_frame_observer import IAudioFrameObserver,AudioFrame
from agora.rtc.audio_pcm_data_sender import PcmAudioFrame
from agora.rtc.rtc_connection import RTCConnConfig
from observer.mi_connection_observer import MiConnectionObserver
from observer.mi_audio_frame_observer import MiAudioFrameObserver
from observer.mi_local_user_observer import MiLocalUserObserver
from observer.mi_video_frame_observer import MiVideoFrameObserver

class ExampleAudioFrameObserver(IAudioFrameObserver):
    def __init__(self, pcm_data_sender, loop) -> None:
        self._loop = loop
        self._pcm_data_sender = pcm_data_sender

    def on_record_audio_frame(self, agora_local_user ,channelId, frame):
        logger.info(f"on_record_audio_frame")
        return 0
    def on_playback_audio_frame(self, agora_local_user, channelId, frame):
        logger.info(f"on_playback_audio_frame")
        return 0
    def on_ear_monitoring_audio_frame(self, agora_local_user, frame):
        logger.info(f"on_ear_monitoring_audio_frame")
        return 0

    def on_playback_audio_frame_before_mixing(self, agora_local_user, channelId, uid, audio_frame:AudioFrame):
        # logger.info(f"on_playback_audio_frame_before_mixing:{threading.current_thread().ident}, {len(audio_frame.buffer)}")
        frame = PcmAudioFrame()
        frame.data = audio_frame.buffer
        frame.timestamp = 0
        frame.samples_per_channel = 160
        frame.bytes_per_sample = 2
        frame.number_of_channels = 1
        frame.sample_rate = 16000
        self._loop.call_soon_threadsafe(
            self._pcm_data_sender.send_audio_pcm_data,frame
        )
        return 1

    def on_get_audio_frame_position(self, agora_local_user):
        logger.info(f"on_get_audio_frame_position")
        return 0


async def run_example():
    loop = asyncio.get_event_loop()
    _exit = loop.create_future()
    def handle_signal():
        _exit.set_result(None)
    loop.add_signal_handler(signal.SIGINT, handle_signal)
    loop.add_signal_handler(signal.SIGTERM, handle_signal)

    #---------------1. Init SDK
    config = AgoraServiceConfig()
    config.appid ="20338919f2ca4af4b1d7ec23d8870b56"
    config.log_path = get_log_path_with_filename(os.path.splitext(__file__)[0])
    print("qidebug, log path", config.log_path)
    agora_service = AgoraService()
    agora_service.initialize(config)

    #---------------2. Create Connection
    con_config = RTCConnConfig(
        client_role_type=ClientRoleType.CLIENT_ROLE_BROADCASTER,
        channel_profile=ChannelProfileType.CHANNEL_PROFILE_LIVE_BROADCASTING,
    )
    connection = agora_service.create_rtc_connection(con_config)

    media_node_factory = agora_service.create_media_node_factory()
    conn_observer = MiConnectionObserver()
    connection.register_observer(conn_observer)
    connection.connect("", "qitest","9999999")

    local_user = connection.get_local_user()
    local_user.set_audio_scenario(AudioScenarioType.AUDIO_SCENARIO_CHORUS)
    local_user.set_playback_audio_frame_before_mixing_parameters(1, 16000)
    local_user.subscribe_all_audio()
    localuser_observer = MiLocalUserObserver()
    local_user.register_local_user_observer(localuser_observer)

    pcm_data_sender = media_node_factory.create_audio_pcm_data_sender()
    audio_track = agora_service.create_custom_audio_track_pcm(pcm_data_sender)
    audio_track.set_enabled(1)
    local_user.publish_audio(audio_track)

    audio_frame_observer = ExampleAudioFrameObserver(pcm_data_sender, loop)
    local_user.register_audio_frame_observer(audio_frame_observer)

    await _exit
    local_user.unpublish_audio(audio_track)
    audio_track.set_enabled(0)
    connection.unregister_observer()
    connection.disconnect()
    connection.release()
    logger.info("connection release")

    agora_service.release()
    logger.info("agora_service release")


if __name__ == "__main__":
    asyncio.run(run_example())