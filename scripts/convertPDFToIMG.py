# import office
#
# # 一行代码，实现转换
# office.pdf.pdf2imgs(
#     pdf_path='E:/File/公司/公司营业执照.pdf',
#     out_dir='./'
# )
# # 参数说明：
# # pdf_path = 你的PDF文件的地址
# # out_dir = 转换后的图片存放地址，可以不填，默认是PDF的地址

import fitz

'''
# 将PDF转化为图片
pdfPath pdf文件的路径
imgPath 图像要保存的文件夹
zoom_x x方向的缩放系数
zoom_y y方向的缩放系数
rotation_angle 旋转角度
'''


def pdf_image(pdfPath, imgPath, zoom_x, zoom_y, rotation_angle):
    # 打开PDF文件
    pdf = fitz.open(pdfPath)
    # 逐页读取PDF
    for pg in range(0, pdf.pageCount):
        page = pdf[pg]
        # 设置缩放和旋转系数
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotation_angle)
        pm = page.getPixmap(matrix=trans, alpha=False)
        # 开始写图像
        pm.writePNG(imgPath + str(pg) + ".png")
    pdf.close()

pdf_path='E:/File/公司/公司营业执照.pdf'
out_dir='./'
pdf_image(pdf_path, out_dir, 5, 5, 0)