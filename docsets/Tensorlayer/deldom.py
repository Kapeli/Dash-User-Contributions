from bs4 import BeautifulSoup
import os,re



def changeandsave(url):  #更改指定div并保存到源文件

    try:
        with open(url, encoding='utf-8') as fp:
            text = BeautifulSoup(fp, 'lxml')
            dom_save = text.find(class_='rst-content')
            dom_first = text.find(class_='wy-grid-for-nav')
            dom_first.clear()
            dom_first.insert(0, dom_save)
            f_obj = open(url, 'wb')
            f_obj.write(text.encode('utf-8'))
            f_obj.close()
    except :
        print('file error',url)
def main(dirname):

    for root, dirs, files in os.walk(dirname):  #遍历文件夹下所有html文件

        for file in files:

            result =re.search('.*?html',file)

            if result:
                print(os.path.join(root, file))
                url=os.path.join(root, file);
                changeandsave(url)

        print('----------------')


if __name__ == '__main__':
    main(r'./')
