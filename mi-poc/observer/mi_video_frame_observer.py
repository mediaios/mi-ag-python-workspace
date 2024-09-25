from agora.rtc.video_frame_observer import IVideoFrameObserver,VideoFrame
from utils.mi_video_process import save_yuv_to_jpeg,yuv420_to_rgb
import time
import os
import subprocess
import base64
import logging

logger = logging.getLogger(__name__)
class MiVideoFrameObserver(IVideoFrameObserver):
    def __init__(self):
        super(MiVideoFrameObserver, self).__init__()

    def on_frame(self, video_frame_observer, channel_id, remote_uid, frame: VideoFrame):
        print("QiDebug, MiVideoFrameObserver , on_frame:", video_frame_observer, channel_id, remote_uid, frame.width,
              frame.height, frame.y_stride, frame.u_stride, frame.v_stride, len(frame.y_buffer), len(frame.u_buffer),
              len(frame.v_buffer))

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

        print(f"QiDebug, Buffer size: {len(buffer)} bytes")

        # 调用 extract_first_frame_to_base64，将 YUV 数据转换为 JPEG 的 Base64 编码
        base64_jpeg = extract_first_frame_to_base64(buffer, frame.width, frame.height)

        if base64_jpeg:
            print(f"QiDebug, Extracted frame as Base64 JPEG: {base64_jpeg[:100]}...")  # 打印前100个字符用于检查
        else:
            print("QiDebug, Failed to extract JPEG from YUV")

        return 1

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
