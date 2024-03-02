import sys
import csv
import time  
from datetime import datetime
from fake_headers import Headers
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
class InstagramBot():
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--log-level=3")
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument("--disable-popup-blocking")
        self.chrome_options.add_argument("--user-agent={}".format(Headers().generate()["User-Agent"]))
        self.chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.chrome_options)
        self.csvScrapedData = [["description", "weight", "location", "user", "time", "image"]]
        self.hashtag = ""
      
    def signIn(self, email, password):
        print("Signing In")
        self.email = email
        self.password = password
        self.browser.get('https://www.instagram.com/accounts/login/')
        emailInput = self.browser.find_elements_by_css_selector('form input')[0]
        passwordInput = self.browser.find_elements_by_css_selector('form input')[1]
        emailInput.send_keys(self.email)
        passwordInput.send_keys(self.password)
        passwordInput.send_keys(Keys.ENTER)
        time.sleep(2)
    
    def scrape(self, url):
        self.browser.get(url)
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elements = self.browser.find_element(By.XPATH, "//div[@class='v1Nh3 kIKUG  _bz0w']")
        # elements = self.browser.find_elements_by_xpath("//div[@class='v1Nh3 kIKUG  _bz0w']")
        hrefElements = self.browser.find_element(By.XPATH, "//div[@class='v1Nh3 kIKUG  _bz0w']/a")
        elements_link = [x.get_attribute("href") for x in hrefElements]
        for elements in elements_link:
            self.scrapePost(elements)
 
    def scrapePost(self, url):
        self.browser.get(url)
        print("Scraping Post: " + url)
        try: 
            location_element = self.browser.find_element(By.XPATH,"//a[@class='O4GlU']").text
            location_element = location_element.replace(",", " ")
            user_element = self.browser.find_element(By.XPATH,"//a[@class='FPmhX notranslate nJAzx']")
            user_element_text = user_element.text
            user_element_text = user_element_text.replace(",", " ")
            user_element_link = user_element.get_attribute("href")
            try:
                desc_element = self.browser.find_element(By.XPATH,"//div[@class='C4VMK']/span")
                desc_text = desc_element.text
                desc_text = desc_text.replace("\n", " ")
                desc_text = desc_text.replace(",", " ")
            except:
                desc_text = " "
            try: 
                timestamp_element = self.browser.find_element(By.XPATH,"//div[@class='k_Q0X NnvRN']/a/time")
                timestamp = timestamp_element.get_attribute("datetime")
                timestamp = timestamp.replace("\n", " ")
                timestamp = timestamp.replace(",", " ")
            except:
                timestamp = " "
            try:
                likes_element = self.browser.find_element(By.XPATH,"//a[@class='zV_Nj']/span").text
                likes_element = likes_element.replace(",", "")
                no_of_likes = int(likes_element)
                followerCount = self.findFollowerCount(user_element_link)
                weight = no_of_likes/followerCount
            except:
                weight = 0
            image_url = self.findImage()
            self.scrapedData = [desc_text, weight ,location_element, user_element_text, timestamp, image_url]
            print(self.scrapedData)
            self.csvScrapedData.append(self.scrapedData)
        except:
            pass
      
       
    def findImage(self):
        image_element = self.browser.find_element(By.XPATH,"//div[@class='KL4Bh']/img")
        image_element_link = image_element.get_attribute("src")
        return image_element_link

   
    def findFollowerCount(self, userURL):
        self.browser.get(userURL)
        followers_count_int = 0 
        try:
            count_element = self.browser.find_element(By.XPATH,"//span[@class='g47SY ']")
            followers_count = count_element[1].get_attribute("title")
            followers_count = followers_count.replace(",", "")
            followers_count_int = int(followers_count)
        except:
            pass    
        return followers_count_int
    
    
    def scrapeWithHashtags(self, hashtags):
        for hashtag in hashtags:
            self.hashtag = hashtag
            print("-----------Scraping the hashtag '" + hashtag +"' -----------")
            url = 'https://www.instagram.com/explore/tags/' + hashtag
            self.scrape(url)
        
    def exportCSVFile(self):
        csv.register_dialect('myDialect', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        with open('csvScrapedData.csv', 'w') as f:
            writer = csv.writer(f, dialect='myDialect')
            for row in self.csvScrapedData:
                writer.writerow(row)
        f.close()
      
scrape_type = input("Do you want to scrape any private posts [y/n]:\n")
hashtags = ['dog']
bot = InstagramBot()

if scrape_type == "y":
    username = input("What's your email?\n")
    password = input("What's your password?\n")
    bot.signIn(username, password)
elif scrape_type == "n":
    pass
else:
    sys.exit("No valid Input")

bot.scrapeWithHashtags(hashtags)
bot.exportCSVFile()
