from selenium import webdriver
import time
import requests,bs4,json
import time
import urllib.request
from loguru import logger
import os
import img2pdf
#----------------------------------------------
headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            }

url_mh = "https://www.copymanga.com"
#----------------------------------------------
def download_img(img_url,filnem):
    request = urllib.request.Request(img_url, headers=headers)
    try:
        response = urllib.request.urlopen(request)
        filename = filnem
        if (response.getcode() == 200):
            with open(filename, "wb") as f:
                f.write(response.read()) 
            return filename
    except:
        return "failed"

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
    logger.info(f"创建漫画第 "+str(hua)+ " 话文件夹")
    try:
        os.mkdir("./dl-img/"+str(wjj)+"/"+str(hua))
    except:
        pass
    url = str(urll)

    chrome_options = webdriver.ChromeOptions() 
    chrome_options.add_argument("--incognito")
    chrome_options.set_headless()
    driver = webdriver.Chrome(chrome_options=chrome_options)
    
    logger.info("开始模拟浏览器访问")
    driver.get(url)

    try:
        for i in range(0,500): #模拟浏览器滑动操作
            js = "window.scrollTo(0,"+str(i)+")"
            driver.execute_script(js)
    except:
        pass
    logger.info("模拟浏览器滑动操作")
    driver.set_page_load_timeout(60)
    time.sleep(5)
    logger.info("获取网页图片列表")
    noStarchSoup = bs4.BeautifulSoup(driver.page_source,"html.parser")
    #关闭浏览器
    driver.quit()
    elems_ul = noStarchSoup.select('ul')[0]
    elems = elems_ul.select('img')

    logger.info("获取成功!共 "+str(len(elems))+" 张,开始下载图片")
    for b in range(0,len(elems)):
        html_img = elems[b]
        dl_json = json.loads(json.dumps(html_img.attrs))
        #print(dl_json["data-src"])
        dl_img_url = dl_json["data-src"]
        out = download_img(dl_img_url,"./dl-img/"+str(wjj)+"/"+str(hua)+"/"+str(b+1)+".jpg")
        logger.info(str(out)+" 下载完成")
        time.sleep(0.5)
    logger.info(f"漫画第 "+str(hua)+ " 话下载完成")

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
        f.write(img2pdf.convert(list_out_nub))
        f.close()

if __name__ == '__main__':
    mh_nub = 1
    mh_url = str(input("请输入漫画地址:"))
    print("正在获取漫画信息...")
    mh_name = get_name(mh_url)
    print("漫画名字为 "+mh_name)
    print("创建文件夹 "+mh_name)
    os.mkdir("./dl-img/"+str(mh_name))
    os.mkdir("./dl-img/"+str(mh_name)+"/pdf")
    print("开始下载...")
    mh_url = get_rk(mh_url)
    #next_url = ""
    while mh_url != False:
        dl_manhua(mh_url,mh_name,str(mh_nub))
        make_pdf(mh_name,str(mh_nub))
        mh_url = next_mh(mh_url)
        mh_nub +=1
    os.system('TASKKILL /F /IM chromedriver.exe')



