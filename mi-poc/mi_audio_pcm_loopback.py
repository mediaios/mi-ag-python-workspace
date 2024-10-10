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
    def __init__(self, pcm_data_sender, loop,enable_delay_mode=True) -> None:
        self._loop = loop
        self._pcm_data_sender = pcm_data_sender
        # for delay test to verify sdk's inner delay
        self._last_push_time = time.time() * 1000  # in ms
        self._data = bytearray()
        self._is_delay_pushed = False
        self._enable_delay_mode = enable_delay_mode

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
        # check do push immediately or not
        now = time.time() * 1000  # in ms
        # check diff with last push
        diff = now - self._last_push_time
        if diff > 18 * 10:  # 180ms
            self._is_delay_pushed = False

        # if mode is false, then force delayed_push to true
        if self._enable_delay_mode == False:
            self._is_delay_pushed = True

        # do op
        if self._is_delay_pushed == False:
            packs = len(self._data) // (320)  #每10ms产生的数据量是 320 字节，即 samples = 16000/1000*10ms = 160; bufferSize = samples*bitPerSample/8*channels = 160*2 = 320
            if packs < 18:
                self._data += audio_frame.buffer
            else:  # push all data and set to TRUE
                frame = PcmAudioFrame()
                frame.data = self._data
                frame.timestamp = 0
                frame.samples_per_channel = 160 * packs
                frame.bytes_per_sample = 2
                frame.number_of_channels = 1
                frame.sample_rate = 16000
                self._loop.call_soon_threadsafe(
                    self._pcm_data_sender.send_audio_pcm_data, frame
                )
                self._is_delay_pushed = True
                self._last_push_time = now
                self._data.clear()
                print("push chunk: =", packs)
        else:  # push immediately
            # do immediately
            frame = PcmAudioFrame()
            frame.data = audio_frame.buffer
            frame.timestamp = 0
            frame.samples_per_channel = 160
            frame.bytes_per_sample = 2
            frame.number_of_channels = 1
            frame.sample_rate = 16000
            self._loop.call_soon_threadsafe(
                self._pcm_data_sender.send_audio_pcm_data, frame
            )
            self._last_push_time = now
        return 1

    def on_get_audio_frame_position(self, agora_local_user):
        logger.info(f"on_get_audio_frame_position")
        return 0


def push_init_pcm(pcm_sender):
    packs = 18
    data = bytearray(320 * packs)
    frame = PcmAudioFrame()
    frame.data = data
    frame.timestamp = 0
    frame.samples_per_channel = 160 * packs
    frame.bytes_per_sample = 2
    frame.number_of_channels = 1
    frame.sample_rate = 16000
    pcm_sender.send_audio_pcm_data(frame)

    pass

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

    # added by wei to push 160ms pcm data
    # push_init_pcm(pcm_data_sender)
    # time.sleep(0.2)

    audio_frame_observer = ExampleAudioFrameObserver(pcm_data_sender, loop, False)
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