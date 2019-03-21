#import shutil
#import os
#
#image_paths = []
#for directory, folders, files in os.walk('/home/vcaadmin/zhuangwu/scene_test/34k_test_371'):
#    for file in files:
#        id_and_name = file.split('.')
#        if id_and_name[1] == 'jpg' and int(id_and_name[0]) % 50 == 0:
#            image_paths.append(os.path.join(directory, file))
#            
#print(len(image_paths), image_paths[0])

print(1280 // 300)
