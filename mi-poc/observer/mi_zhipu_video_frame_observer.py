import asyncio

from agora.rtc.video_frame_observer import IVideoFrameObserver,VideoFrame
from utils.mi_video_process import save_yuv_to_jpeg,yuv420_to_rgb
import time
import os
import subprocess
import base64
import logging

class VideoH264Frame:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.buf_ = None

logger = logging.getLogger(__name__)
class MiZhiPuVideoFrameObserver(IVideoFrameObserver):
    def __init__(self):
        super(MiZhiPuVideoFrameObserver, self).__init__()

    def on_frame(self, video_frame_observer, channel_id, remote_uid, frame: VideoFrame):
        print("QiDebug, MiVideoFrameObserver , on_frame:", video_frame_observer, channel_id, remote_uid, frame.width,
              frame.height, frame.y_stride, frame.u_stride, frame.v_stride, len(frame.y_buffer), len(frame.u_buffer),
              len(frame.v_buffer))

        h264_frame = self.get_frame(frame)
        return 0
        # y_stride = 720;   u_stride=360; v_stride=360
        # try:
        #     if time.time() > self.event_handler.last_video_time + 0.3:
        #         self.event_handler.last_video_time = time.time()
        #         h264_frame = self.get_frame(frame)
        #         asyncio.get_event_loop().run_until_complete(self.event_handler.video_cache.set([h264_frame]))
        #         logger.info(f"[Python] on remote video cache: {remote_uid}")
        #     return 1
        # except Exception as e:
        #     logger.error(f"[Python] on remote video frame error: {e}")
        #     return 0

    def get_frame(self, frame: VideoFrame) -> VideoH264Frame:
        h264Frame = VideoH264Frame()
        h264Frame.width = frame.width
        h264Frame.height = frame.height

        # 创建用于存储YUV数据的缓冲区
        buffer = bytearray()

        # 计算Y和UV数据的大小
        y_size = frame.y_stride * frame.height
        uv_size = (frame.u_stride * frame.height // 2)

        # 将Y、U、V数据写入缓冲区
        buffer.extend(frame.y_buffer[:y_size])
        buffer.extend(frame.u_buffer[:uv_size])
        buffer.extend(frame.v_buffer[:uv_size])

        h264Frame.buf_ = bytes(buffer)
        logger.info(f"agora debug, get_frame buffer size: {len(buffer)} bytes")
        logger.info(f"agora debug, get_frame width: {frame.width}, height: {frame.height}")
        logger.info(
            f"agora debug, get_frame y_buffer size: {len(frame.y_buffer)}, u_buffer: {len(frame.u_buffer)}, v_buffer: {len(frame.v_buffer)}")

        # 写入到当前目录的test.yuv文件中
        file_path = os.path.join(os.getcwd(), 'test2.yuv')  # 获取当前目录路径
        with open(file_path, 'ab') as f:  # 'ab' 表示以二进制追加模式写入
            f.write(buffer)

        print(f"QiDebug, Buffer size: {len(buffer)} bytes")

        # 调用 extract_first_frame_to_base64，将 YUV 数据转换为 JPEG 的 Base64 编码
        base64_jpeg = extract_first_frame_to_base64(buffer, frame.width, frame.height)

        if base64_jpeg:
            print(f"QiDebug, Extracted frame as Base64 JPEG: {base64_jpeg[:100]}...")  # 打印前100个字符用于检查
        else:
            print("QiDebug, Failed to extract JPEG from YUV")


        return h264Frame

def extract_first_frame_to_base64(yuv_bytes, width, height):
    # Prepare the FFmpeg command
    command = [
        "ffmpeg",
        "-f", "rawvideo",  # 输入是原始视频数据
        "-pix_fmt", "yuv420p",  # YUV420P 像素格式
        "-s", f"{width}x{height}",  # 视频的宽高
        "-i", "pipe:0",  # 从标准输入读取数据
        "-vframes", "1",  # 只提取一帧
        "-f", "mjpeg",  # 输出为 MJPEG 格式
        "pipe:1",  # 将结果输出到标准输出
    ]

    # Run FFmpeg command
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Communicate with the process (send YUV data to FFmpeg and get the output)
    out, err = process.communicate(input=yuv_bytes)

    if not out:
        logger.error(f"Failed to extract frame: {err.decode('utf-8')}")
        return ""

    # 生成当前时间的毫秒数作为文件名
    current_time_ms = int(time.time() * 1000)
    file_name = f"{current_time_ms}.jpeg"

    print("QiDebug, filenName: ",file_name)
    # 将 JPEG 数据保存到文件
    with open(file_name, 'wb') as f:
        f.write(out)

    # Convert the output (JPEG frame) to Base64
    base64_encoded = base64.b64encode(out)

    return base64_encoded.decode("utf-8")

