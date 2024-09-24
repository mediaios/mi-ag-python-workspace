from agora.rtc.video_frame_observer import IVideoFrameObserver,VideoFrame

import os
class MiVideoFrameObserver(IVideoFrameObserver):
    def __init__(self):
        super(MiVideoFrameObserver, self).__init__()

    def on_frame(self, video_frame_observer, channel_id, remote_uid, frame: VideoFrame):
        print("QiDebug, MiVideoFrameObserver , on_frame:", video_frame_observer, channel_id, remote_uid, frame.width,
              frame.height, frame.y_stride, frame.u_stride, frame.v_stride, len(frame.y_buffer), len(frame.u_buffer),
              len(frame.v_buffer))

        # print("QiDebug, MiVideoFrameObserver on_frame:", video_frame_observer, channel_id, remote_uid, frame)

        # file_path = os.path.join(log_folder, channel_id + "_" + remote_uid + '.yuv')
        #
        # # 整体的size是 w*h*3/2
        #
        # y_size = frame.y_stride * frame.height
        # uv_size = (
        #             frame.u_stride * frame.height // 2) if frame.u_stride == frame.v_stride else frame.u_stride * frame.height // 2 + frame.v_stride * frame.height // 2
        #
        # print("DYSVideoFrameObserver on_frame:", y_size, uv_size)
        # with open(file_path, 'ab') as f:
        #     f.write(frame.y_buffer[:y_size])
        #     f.write(frame.u_buffer[:uv_size // 2])
        #     f.write(frame.v_buffer[:uv_size // 2])

        # 创建用于存储YUV数据的缓冲区
        buffer = bytearray()

        # 计算Y和UV数据的大小
        y_size = frame.y_stride * frame.height
        uv_size = (frame.u_stride * frame.height // 2)

        # 将Y、U、V数据写入缓冲区
        buffer.extend(frame.y_buffer[:y_size])
        buffer.extend(frame.u_buffer[:uv_size])
        buffer.extend(frame.v_buffer[:uv_size])

        # 写入到当前目录的test.yuv文件中
        file_path = os.path.join(os.getcwd(), 'test.yuv')  # 获取当前目录路径
        with open(file_path, 'ab') as f:  # 'ab' 表示以二进制追加模式写入
            f.write(buffer)

        # 这里你可以继续操作缓冲区中的数据，例如传递给其他函数或处理
        print(f"QiDebug, Buffer size: {len(buffer)} bytes")
        return 1
    #
    # def on_user_video_track_subscribed(self, agora_local_user, user_id, info, agora_remote_video_track):
    #     print("DYSVideoFrameObserver on_user_video_track_subscribed:", agora_local_user, user_id, info,
    #           agora_remote_video_track)
    #     return 0

    # def on_user_video_track_subscribed(self, agora_local_user, user_id, agora_remote_video_track:RemoteVideoTrack, video_track_info):
    #     print("DYSVideoFrameObserver _on_user_video_track_subscribed:", agora_local_user, user_id, agora_remote_video_track, video_track_info)
    # agora_remote_video_track.register_video_encoded_image_receiver(video_encoded_image_receiver)