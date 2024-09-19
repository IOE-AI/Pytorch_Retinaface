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
random.seed(42)  # 设置随机种子
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
            # 从 point.tag 中提取坐标
            if point.tag.startswith('x'):
                x = int(point.text)
            elif point.tag.startswith('y'):
                y = int(point.text)
                points.append((x, y))  # 将 (x, y) 坐标添加到列表中
        
        # 计算边界框
        xmin = min(p[0] for p in points)
        ymin = min(p[1] for p in points)
        xmax = max(p[0] for p in points)
        ymax = max(p[1] for p in points)
        
        # 计算宽高
        w = xmax - xmin
        h = ymax - ymin
        
        # 计算四个角点坐标
        x1, y1 = points[0]  # 左上角
        x2, y2 = points[1]  # 右上角
        x3, y3 = points[2]  # 右下角
        x4, y4 = points[3]  # 左下角
        
        # 写入标签文件
        with open(label_file, 'a') as f:
            f.write(f"# {img_name}\n")
            f.write(f"{xmin} {ymin} {w} {h} {x1} {y1} 0.0 {x2} {y2} 0.0 {x3} {y3} 0.0 {x4} {y4} 0.0\n")

# 生成训练和验证标签文件
train_label_file = './widerface/train/label.txt'
val_label_file = './widerface/val/wider_val.txt'

for img in train_imgs:
    process_xml_to_txt(os.path.join(output_train_label_dir, img.replace('.jpg', '.xml')), img, train_label_file)

# 生成验证文件名列表，不包含标签信息
with open(val_label_file, 'w') as f:
    for img in val_imgs:
        f.write(f"{img}\n")  # 只写入文件名，不写入标签信息
print('Done!')