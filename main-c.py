import time
import requests,bs4,json
import urllib.request
from loguru import logger
import os
import img2pdf
from threading import Thread
from selenium import webdriver
#----------------------------------------------
headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            }

url_mh = "https://www.copymanga.com"
#----------------------------------------------
def download_img(img_url,filnem):
    request = urllib.request.Request(img_url, headers=headers)
    logger.info("开始下载 "+str(filnem))
    try:
        response = urllib.request.urlopen(request)
        filename = filnem
        if (response.getcode() == 200):
            with open(filename, "wb") as f:
                f.write(response.read()) 
                logger.info(str(filnem)+" 下载完成!")
            return filename
    except Exception as oo:
        logger.error(f"图片下载遇到错误 "+str(oo))
        return "failed"

def get_mhlist(url):
    list_mhname = []

    chrome_options = webdriver.ChromeOptions() 
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    logger.info("模拟浏览器访问")
    driver.get(url)
    driver.set_page_load_timeout(60)

    logger.info("获取漫画列表")
    noStarchSoup = bs4.BeautifulSoup(driver.page_source,"html.parser")
    #关闭浏览器
    driver.quit()

    elems = noStarchSoup.select('div[class="tab-pane fade show active"]')[0]
    elems = elems.select('ul')[0]
    elems = elems.select('a')
    for b in range(0,len(elems)):
        json_inup = elems[b]
        list_josn = json.loads(json.dumps(json_inup.attrs))
        list_mhname.append(str(list_josn["title"]))
    #elems = json.loads(json.dumps(elems.attrs))
    return list_mhname

def get_document(url):
    try:
        get = requests.get(url, headers=headers)
        data = get.content
        get.close()
    except:
        time.sleep(3)
        try:
            get = requests.get(url)
            data = get.content
            get.close()
        except:
            time.sleep(3)
            get = requests.get(url)
            data = get.content
            get.close()
    return data

def dl_manhua(urll,wjj,hua):

    logger.info(f"创建漫画 "+str(hua)+ " 文件夹")
    try:
        os.mkdir("./dl-img/"+str(wjj)+"/"+str(hua))
    except:
        pass
    url = str(urll)

    chrome_options = webdriver.ChromeOptions() 
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)

    logger.info("开始模拟浏览器访问")
    driver.get(url)

    logger.info("模拟浏览器滑动操作")
    try:
        for i in range(0,500): #模拟浏览器滑动操作
            js = "window.scrollTo(0,"+str(i)+")"
            driver.execute_script(js)
    except:
        pass
    
    driver.set_page_load_timeout(60)

    logger.info("获取网页图片列表")
    noStarchSoup = bs4.BeautifulSoup(driver.page_source,"html.parser")
    #关闭浏览器
    driver.quit()

    elems_ul = noStarchSoup.select('ul')[0]
    elems = elems_ul.select('img')
    logger.info("获取成功!共 "+str(len(elems))+" 张,开始下载图片")
    thread_list = []
    for b in range(len(elems)):
        html_img = elems[b]
        dl_json = json.loads(json.dumps(html_img.attrs))
        dl_img_url = dl_json["data-src"]
        t1 = Thread(target=download_img, args=(dl_img_url,"./dl-img/"+str(wjj)+"/"+str(hua)+"/"+str(b+1)+".jpg"))  # 定义线程t1，线程任务为调用task1函数，task1函数的参数是6
        #t1.start()
        thread_list.append(t1)
        time.sleep(0.5)
    
    for t in thread_list:
        t.setDaemon(True)
        t.start()
    for t in thread_list:
        t.join() 

    logger.info(f"漫画 "+str(hua)+ " 下载完成")

def get_rk(url):
    noStarchSoup = bs4.BeautifulSoup(get_document(url),"html.parser")
    elems = noStarchSoup.select('li')[7]
    elems = elems.select('a')[0]
    elems = json.loads(json.dumps(elems.attrs))
    dl_url = url_mh+str(elems["href"])
    return dl_url

def get_name(url):
    noStarchSoup = bs4.BeautifulSoup(get_document(url),"html.parser")
    elems = noStarchSoup.select('ul')[0]
    elems = elems.select('h6')[0]
    elems = json.loads(json.dumps(elems.attrs))
    return elems["title"]

def next_mh(url):
    noStarchSoup = bs4.BeautifulSoup(get_document(url),"html.parser")
    elems_next = noStarchSoup.select('div[class="comicContent-next"]')[0]
    s_elems = elems_next.select('a')[0]
    next_json = json.loads(json.dumps(s_elems.attrs))
    if next_json["href"] == '':
        return False
    else:
        return url_mh+str(next_json["href"])

def make_pdf(wjj,hua):
    fil_rl = "./dl-img/"+wjj+"/"+hua
    list_nub = os.listdir(fil_rl)
    list_out_nub = []
    for i in range(0,len(list_nub)):
        list_out_nub.append(fil_rl+"/"+str(i+1)+".jpg")

    with open("./dl-img/"+wjj+"/pdf/"+hua+".pdf", "wb") as f:
        try:
            f.write(img2pdf.convert(list_out_nub))
            f.close()
        except Exception as err:
            logger.error(f"PDF生成遇到错误 "+str(err))

if __name__ == '__main__':
    try:
        mh_nub = 1
        mh_url = str(input("请输入漫画地址:"))
        print("正在获取漫画信息...")
        mh_name = get_name(mh_url)
        mhlist_name = get_mhlist(mh_url)
        print("漫画名字为 "+mh_name)
        print("创建文件夹 "+mh_name)
        os.mkdir("./dl-img/"+str(mh_name))
        os.mkdir("./dl-img/"+str(mh_name)+"/pdf")
        print("开始下载...")
        mh_url = get_rk(mh_url)
        #next_url = ""
        while mh_url != False:
            dl_manhua(mh_url,mh_name,str(mhlist_name[mh_nub-1]))
            make_pdf(mh_name,str(mhlist_name[mh_nub-1]))
            mh_url = next_mh(mh_url)
            mh_nub +=1
        print("漫画下载完成!")
    except Exception as out_err:
        logger.error(f"主程序遇到错误 "+str(out_err))




