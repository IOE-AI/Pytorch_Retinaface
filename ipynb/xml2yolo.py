import os
import shutil
import random
import xml.etree.ElementTree as ET

# 定义路径
input_img_dir = './origin/Images/'
input_xml_dir = './origin/Annotations/'
output_train_img_dir = './yolo/train/images/'
output_val_img_dir = './yolo/val/images/'
output_train_label_dir = './yolo/train/label/'
output_val_label_dir = './yolo/val/label/'

# 创建输出目录
os.makedirs(output_train_img_dir, exist_ok=True)
os.makedirs(output_val_img_dir, exist_ok=True)
os.makedirs(output_train_label_dir, exist_ok=True)
os.makedirs(output_val_label_dir, exist_ok=True)

# 获取所有图像文件
img_files = [f for f in os.listdir(input_img_dir) if f.endswith('.jpg')]
random.shuffle(img_files)

# 按 9:1 的比例分割数据
split_index = int(len(img_files) * 0.9)
train_imgs = img_files[:split_index]
val_imgs = img_files[split_index:]

# 定义类别标签到索引的映射字典
label_to_index = {
    'blue': 0,
    'green': 1,
    'other': 2,
    'white': 3,
    'yellow': 4
}

def convert_xml_to_txt(xml_file, output_txt_file, label_to_index):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # 获取图像尺寸
    img_width = int(root.find('size/width').text)
    img_height = int(root.find('size/height').text)

    # 处理每个对象
    for obj in root.findall('object'):
        label = obj.find('name').text
        label_index = label_to_index.get(label, -1)  # 获取标签索引
        polygon = obj.find('polygon')
        points = [(int(polygon.find(f'x{i+1}').text), int(polygon.find(f'y{i+1}').text)) for i in range(5)]
        
        # 计算边界框
        xmin = min(pt[0] for pt in points)
        ymin = min(pt[1] for pt in points)
        xmax = max(pt[0] for pt in points)
        ymax = max(pt[1] for pt in points)

        # 计算中心点和宽高
        width = xmax - xmin
        height = ymax - ymin
        center_x = xmin + width / 2
        center_y = ymin + height / 2
        
        # 归一化
        norm_center_x = center_x / img_width
        norm_center_y = center_y / img_height
        norm_width = width / img_width
        norm_height = height / img_height
        
        # 关键点坐标
        pt1x, pt1y = points[0][0] / img_width, points[0][1] / img_height  # 左上
        pt2x, pt2y = points[1][0] / img_width, points[1][1] / img_height  # 右上
        pt3x, pt3y = points[2][0] / img_width, points[2][1] / img_height  # 右下
        pt4x, pt4y = points[3][0] / img_width, points[3][1] / img_height  # 左下
        
        # 写入 TXT 文件
        with open(output_txt_file, 'a') as f:
            f.write(f"{label_index} {norm_center_x} {norm_center_y} {norm_width} {norm_height} "
                     f"{pt1x} {pt1y} {pt2x} {pt2y} {pt3x} {pt3y} {pt4x} {pt4y}\n")

# 移动图像文件
for img in train_imgs:
    shutil.copy(os.path.join(input_img_dir, img), output_train_img_dir)
    # 读取 XML 文件并转换为 TXT 格式
    xml_file = os.path.join(input_xml_dir, img.replace('.jpg', '.xml'))
    if os.path.exists(xml_file):
        txt_file = os.path.join(output_train_label_dir, img.replace('.jpg', '.txt'))
        convert_xml_to_txt(xml_file, txt_file, label_to_index)

for img in val_imgs:
    shutil.copy(os.path.join(input_img_dir, img), output_val_img_dir)
    # 处理验证集的 XML 文件
    xml_file = os.path.join(input_xml_dir, img.replace('.jpg', '.xml'))
    if os.path.exists(xml_file):
        txt_file = os.path.join(output_val_label_dir, img.replace('.jpg', '.txt'))
        convert_xml_to_txt(xml_file, txt_file, label_to_index)

print('Done!')