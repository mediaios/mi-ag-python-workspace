import os
from agora.rtc.audio_frame_observer import IAudioFrameObserver,AudioFrame
class MiAudioFrameObserver(IAudioFrameObserver):
    def __init__(self):
        super(MiAudioFrameObserver, self).__init__()

    # def on_get_playback_audio_frame_param(self, agora_local_user):
    #     audio_params_instance = AudioParams()
    #     return audio_params_instance

    def on_record_audio_frame(self, agora_local_user, channelId, frame):
        print("QiDebug,MiAudioFrameObserver,  on_record_audio_frame")
        return 0

    def on_playback_audio_frame(self, agora_local_user, channelId, frame):
        print("QiDebug,MiAudioFrameObserver, on_playback_audio_frame")
        return 0

    def on_ear_monitoring_audio_frame(self, agora_local_user, frame):
        print("QiDebug,MiAudioFrameObserver, on_ear_monitoring_audio_frame")
        return 0

    def on_playback_audio_frame_before_mixing(self, agora_local_user, channelId, uid, audio_frame: AudioFrame):
        # print("QiDebug,MiAudioFrameObserver, on_playback_audio_frame_before_mixing", audio_frame.type, audio_frame.samples_per_sec, audio_frame.samples_per_channel, audio_frame.bytes_per_sample, audio_frame.channels)
        # 获取当前目录
        current_directory = os.getcwd()
        file_path = os.path.join(current_directory, channelId + "_" + uid + '.pcm')
        print("QiDebug,MiAudioFrameObserver, on_playback_audio_frame_before_mixing", file_path, len(audio_frame.buffer))
        with open(file_path, "ab") as f:
            f.write(audio_frame.buffer)
        return 1

    def on_get_audio_frame_position(self, agora_local_user):
        print("QiDebug,MiAudioFrameObserver, on_get_audio_frame_position")
        return 0
    # def on_get_audio_frame_position(self, agora_local_user):
    #     print("CCC on_get_audio_frame_position")
    #     return 0

    # def on_get_playback_audio_frame_param(self, agora_local_user):
    #     print("CCC on_get_playback_audio_frame_param")
    #     return 0
    # def on_get_record_audio_frame_param(self, agora_local_user):
    #     print("CCC on_get_record_audio_frame_param")
    #     return 0
    # def on_get_mixed_audio_frame_param(self, agora_local_user):
    #     print("CCC on_get_mixed_audio_frame_param")
    #     return 0
    # def on_get_ear_monitoring_audio_frame_param(self, agora_local_user):
    #     print("CCC on_get_ear_monitoring_audio_frame_param")
    #     return 0
