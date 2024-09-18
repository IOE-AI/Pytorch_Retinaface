import os
import shutil
import random
import xml.etree.ElementTree as ET

# 定义路径
input_img_dir = './origin/Images/'
input_xml_dir = './origin/Annotations/'
output_train_img_dir = './widerface/train/images/'
output_val_img_dir = './widerface/val/images/'
output_train_label_dir = './widerface/train/label/'
output_val_label_dir = './widerface/val/label/'

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

# 移动图像文件
for img in train_imgs:
    shutil.copy(os.path.join(input_img_dir, img), output_train_img_dir)
    shutil.copy(os.path.join(input_xml_dir, img.replace('.jpg', '.xml')), output_train_label_dir)

for img in val_imgs:
    shutil.copy(os.path.join(input_img_dir, img), output_val_img_dir)
    shutil.copy(os.path.join(input_xml_dir, img.replace('.jpg', '.xml')), output_val_label_dir)

# 处理标注文件并生成标签
def process_xml_to_txt(xml_file, img_name, label_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for obj in root.findall('object'):
        name = obj.find('name').text
        polygon = obj.find('polygon')
        
        # 提取多边形坐标
        points = []
        for point in polygon:
            points.append((int(point.tag[1:]), int(point.text)))  # 获取 x 和 y 坐标
        
        # 计算边界框
        xmin = min(p[0] for p in points)
        ymin = min(p[1] for p in points)
        xmax = max(p[0] for p in points)
        ymax = max(p[1] for p in points)
        
        # 计算宽高
        w = xmax - xmin
        h = ymax - ymin
        
        # 写入标签文件
        with open(label_file, 'a') as f:
            f.write(f"# {img_name}\n")
            f.write(f"{xmin} {ymin} {w} {h} {xmin} {ymin} 0.0 {xmax} {ymin} 0.0 {xmax} {ymax} 0.0 {xmin} {ymax} 0.0\n")
            
# 生成训练和验证标签文件
train_label_file = './widerface/train/label.txt'
val_label_file = './widerface/val/wider_val.txt'

for img in train_imgs:
    process_xml_to_txt(os.path.join(output_train_label_dir, img.replace('.jpg', '.xml')), img, train_label_file)

for img in val_imgs:
    process_xml_to_txt(os.path.join(output_val_label_dir, img.replace('.jpg', '.xml')), img, val_label_file)

print('Done!')