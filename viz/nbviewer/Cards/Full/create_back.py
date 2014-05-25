# from __future__ import division

from PIL import Image, ImageOps

img = Image.open('back.png')

width, height = img.size
new_width, new_height = int(0.93*width), int(0.93*height)

print 'print image_init\twidth={}\theight={}'.format(width, height)
print 'print image_crop\t\twidth={}\theight={}'.format(new_width, new_height)

left = (width - new_width)/2
top = (height - new_height)/2
right = (width + new_width)/2
bottom = (height + new_height)/2

img_crop = img.crop((left, top, right, bottom))

red1 = '#CC494F'
red2 = '#DB6563'

img_new = ImageOps.expand(img_crop, border=(width-new_width, height-new_height), fill=red1)

img_crop.save('back_crop.jpg')
img_crop.save('back_crop.png')
img_new.save('back_new.png')
