import os
import numpy as np
from PIL import Image


def yuv420_to_rgb(yuv_frame, width, height):
    """
    将YUV420格式的数据转换为RGB格式。
    :param yuv_frame: 包含YUV数据的缓冲区
    :param width: 视频宽度
    :param height: 视频高度
    :return: RGB格式的图像
    """
    # YUV420p格式包含Y（luma），U（chroma），V（chroma）三个平面。
    y_size = width * height
    uv_size = y_size // 4  # U和V的尺寸为Y的四分之一

    # 分离Y、U、V数据
    y = np.frombuffer(yuv_frame[:y_size], dtype=np.uint8).reshape((height, width))
    u = np.frombuffer(yuv_frame[y_size:y_size + uv_size], dtype=np.uint8).reshape((height // 2, width // 2))
    v = np.frombuffer(yuv_frame[y_size + uv_size:], dtype=np.uint8).reshape((height // 2, width // 2))

    # 将U、V分量扩展到与Y相同的尺寸
    u_upscaled = u.repeat(2, axis=0).repeat(2, axis=1)
    v_upscaled = v.repeat(2, axis=0).repeat(2, axis=1)

    # 计算RGB值
    yuv = np.stack((y, u_upscaled, v_upscaled), axis=-1)
    m = np.array([[1.164, 0.000, 1.596],
                  [1.164, -0.392, -0.813],
                  [1.164, 2.017, 0.000]])
    rgb = np.dot(yuv - [16, 128, 128], m.T).clip(0, 255).astype(np.uint8)

    return rgb


def save_yuv_to_jpeg(yuv_frame, width, height, output_file):
    """
    将YUV数据转换为JPEG并保存。
    :param yuv_frame: 包含YUV数据的缓冲区
    :param width: 视频宽度
    :param height: 视频高度
    :param output_file: 保存JPEG文件的路径
    """
    # 将YUV数据转换为RGB格式
    rgb_image = yuv420_to_rgb(yuv_frame, width, height)

    # 使用Pillow库将RGB数据转换为JPEG并保存
    image = Image.fromarray(rgb_image)
    image.save(output_file, format='JPEG')
    print(f"Saved JPEG image to {output_file}")


# # 示例使用
# # 假设 frame_buffer 包含YUV数据
# file_path = os.path.join(os.getcwd(), 'test.yuv')
# width, height = 640, 480
#
# # 读取YUV数据
# with open(file_path, 'rb') as f:
#     yuv_data = f.read()
#
# # 保存为JPEG
# output_jpeg_path = os.path.join(os.getcwd(), 'output_image.jpeg')
# save_yuv_to_jpeg(yuv_data, width, height, output_jpeg_path)