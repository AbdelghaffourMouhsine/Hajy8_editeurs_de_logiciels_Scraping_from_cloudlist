from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import time , random
import os, re, json, copy
import zipfile
from bs4 import BeautifulSoup

class ItemScraping:
    
    def __init__(self, url=None, proxy=None, with_selenium_grid=False):
        self.url = url
        self.proxy = proxy
        if self.proxy :
            self.PROXY_HOST = proxy["PROXY_HOST"] # rotating proxy or host
            self.PROXY_PORT = proxy["PROXY_PORT"] # port
            self.PROXY_USER = proxy["PROXY_USER"] # username
            self.PROXY_PASS = proxy["PROXY_PASS"] # password
            self.options = self.get_options_for_proxy()
        else:
            self.options = webdriver.ChromeOptions()
            
        self.with_selenium_grid = with_selenium_grid
        if self.with_selenium_grid:
            # IP address and port and server of the Selenium hub and browser options
            self.HUB_HOST = "localhost"
            self.HUB_PORT = 4444
            self.server = f"http://{self.HUB_HOST}:{self.HUB_PORT}/wd/hub"
            self.driver = webdriver.Remote(command_executor=self.server, options=self.options)
        else:
            self.driver = webdriver.Chrome(options=self.options)

        self.driver.maximize_window()

    def quit_driver(self):
        self.driver.quit()

    def get_options_for_proxy(self):
        
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.PROXY_HOST, self.PROXY_PORT, self.PROXY_USER, self.PROXY_PASS)
        
        def get_chrome_options(use_proxy=True, user_agent=None):
            chrome_options = webdriver.ChromeOptions()
            if use_proxy:
                pluginfile = 'proxy_auth_plugin.zip'
        
                with zipfile.ZipFile(pluginfile, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                chrome_options.add_extension(pluginfile)
            if user_agent:
                chrome_options.add_argument('--user-agent=%s' % user_agent)
            
            return chrome_options
        return get_chrome_options()
        
    def click_elem(self, click_elem):
        t=1
        check = 0
        i = 0
        while not check and i<5:
            try:
                click_elem.click()
                time.sleep(t)     ######
                check = 1
            except Exception as e:
                check = 0
            i += 1


    def get_element(self, path_to_elem, from_elem=None, group=False, innerTextLower=None):
        i = 0
        while i<5:
            try:
                if not from_elem :
                    from_elem = self.driver
                
                if not group:
                    elem = from_elem.find_element(By.XPATH, path_to_elem)
                    
                else : # group is True
                    elems = from_elem.find_elements(By.XPATH, path_to_elem)
                    elem = elems
                    if innerTextLower :
                        for e in elems:
                            if str(e.get_attribute("innerText")).strip().lower() == innerTextLower:
                                elem = e
                                break
                                
                    if innerTextLower and type(elem) == list:
                        return {"status": False, "data": f'cannot find an element with this lower innerText : {innerTextLower}' }
                    
                return {"status": True, "data":elem }
                        
            except Exception as e:
                i += 1
                if i == 5:
                    return {"status": False, "data":str(e) }

    ########################################################################################################
    # def get_linkedin_authentication(self, email = 'abdelghaffourmh@gmail.com', pwd = 'abdo12345'):
        
    #     url = 'https://www.linkedin.com/login/fr?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    #     self.driver.get(url)
    #     time.sleep(2)
        
    #     input_username = self.get_element('//*[@id="username"]')
    #     if input_username["status"]:
    #         input_username = input_username["data"]
    #         input_username.send_keys(email)
    #         input_username.send_keys(Keys.ENTER)
    #     else:
    #         print({"status": False, "data":input_username["data"] })
    #     time.sleep(2)

    #     input_password = self.get_element('//*[@id="password"]')
    #     if input_password["status"]:
    #         input_password = input_password["data"]
    #         input_password.send_keys(pwd)
    #         input_password.send_keys(Keys.ENTER)
    #     else:
    #         print({"status": False, "data":input_password["data"] })

    #     print('linkedin_authentication --> yes')
    #     time.sleep(20)

    # ########################################################################################################
    # def extract_linkedin_profiles_of_company_founders_from_company_linkedin_profile_url(self, item):
    #     self.item = item
    #     time.sleep(random.uniform(1,1.5))
    #     try:
    #         if 'company' in str(self.item.startup_linkedin_url) and (str(self.item.profiles) == 'nan' or str(self.item.profiles).strip() == '[]' or str(self.item.profiles).lower() == 'none'):
    #             # print(self.item.startup_linkedin_url, type(self.item.startup_linkedin_url))
        
            
    #             self.driver.get(self.item.startup_linkedin_url)
    #             time.sleep(random.uniform(2,3.5))
    
    #             a_personnes_link = None
    #             a_personnes_button = self.get_element('/html/body/div[6]/div[3]/div/div[2]/div/div[2]/main/div[1]/section/div/div[2]/div[3]/nav/ul/li[5]/a')
    #             if a_personnes_button["status"]:
    #                 a_personnes_button = a_personnes_button["data"]
    #                 if a_personnes_button.text.strip() != 'Personnes':
    #                     a_personnes_link = a_personnes_button.get_attribute('href')
    
    #             if type(a_personnes_button) == dict or a_personnes_button.text.strip() != 'Personnes':
    #                 # print('at else ...')
    #                 time.sleep(random.uniform(1,2.5))
    #                 a_personnes_button = self.get_element('//li/a', group=True)
    #                 if a_personnes_button["status"]:
    #                     a_personnes_button = a_personnes_button["data"]
    #                     for a in a_personnes_button:
    #                         if a.text.strip() == 'Personnes':
    #                             a_personnes_link = a.get_attribute('href')
    #                             break
    #                 else:
    #                     print({"status": False, "data": a_personnes_button["data"] })

    #             #print(f'a_personnes_link : {a_personnes_link}')
    #             if not a_personnes_link :
    #                 #print(f'yeees if not a_personnes_link :')
    #                 Plus_buttons = self.get_element('//button', group=True)
    #                 if Plus_buttons["status"] and len(Plus_buttons["data"])>0 :
    #                     Plus_buttons = Plus_buttons["data"]
    #                     for button in Plus_buttons:
    #                         if str(button.get_attribute("innerText")).strip().lower() == 'plus':
    #                             #print("yeees button.get_attribute(\"innerText\") == 'Plus':")
    #                             self.click_elem(button)
    #                             time.sleep(random.uniform(1,2.5))
    #                             a_personnes_button = self.get_element('//a', group=True)
    #                             if a_personnes_button["status"]:
    #                                 a_personnes_button = a_personnes_button["data"]
    #                                 for a in a_personnes_button:
    #                                     if a.text.strip() == 'Personnes':
    #                                         a_personnes_link = a.get_attribute('href')
    #                                         break
    #                             break
    #                     #print('no Plus button fonded !!!!!!!!!!!!!!!!!!!111')
    #                 else:
    #                     print(f'Plus_buttons : {Plus_buttons["data"]}')
                                
    #             if a_personnes_link:
    #                 self.driver.get(a_personnes_link)
    #                 time.sleep(random.uniform(2,4.5))
                    
    #                 last_height = self.driver.execute_script("return document.body.scrollHeight")
    #                 second = False
    #                 while True:
    #                     # Scroll down to bottom
    #                     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #                     # Wait to load page
    #                     time.sleep(random.uniform(2.5, 4))
    #                     # Calculate new scroll height and compare with total scroll height
    #                     new_height = self.driver.execute_script("return document.body.scrollHeight")
                        
    #                     if new_height == last_height:
                            
    #                         temp = False
    #                         if not temp:
    #                             buttons = self.get_element('//button', group=True)
    #                             if buttons["status"]:
    #                                 buttons = buttons["data"]
    #                                 if len(buttons)>0:
    #                                     for button in buttons:
    #                                         if button.text.lower() == 'afficher plus de résultats':
    #                                             self.click_elem(button)
    #                                             print("yeeeees : if button.text.lower() == 'afficher plus de résultats':")
    #                                             temp = True
                    
    #                         if second and not temp:
    #                             break
    #                         else:
    #                             if not temp:
    #                                 second = True
    #                             time.sleep(random.uniform(1.5,2.5))
                                
    #                     last_height = new_height
                    
    #             personnes_li_s = self.get_element('//div[@class="artdeco-card org-people-profile-card__card-spacing org-people__card-margin-bottom"]/div/div/ul/li', group=True)
    #             profiles = []
    #             if personnes_li_s["status"]:
    #                 personnes_li_s = personnes_li_s["data"]
    #                 # print(f'le nombre de personnes avant extract est: {len(personnes_li_s)}')
    #                 for li in personnes_li_s:
    #                     profile = self.get_personne_profile_from_li(li)
    #                     if profile["status"]:
    #                         # print(profile["data"])
    #                         profiles.append(profile["data"])
    #                 # print(f'le nombre de personnes apres extract est : {len(profiles)}')
    #             else:
    #                 print({"status": False, "data": personnes_li_s["data"] })
    
    #             self.item.profiles = profiles
    #             print(f'{self.item.startup_name} : {len(self.item.profiles)}')
    #             return {"status": True, "data": self.item }
                            
    #         else:
    #             return {"status": True, "data": self.item }
                
    #     except Exception as e:
    #         print(f'ERRRRRRRRRRRRRRRRRRRRRRRROR: ({self.item.startup_linkedin_url},{type(self.item.startup_linkedin_url)}) {e}')
    #         ExceptionStorage(self.item, str(e))
    #         return {"status": False, "data": self.item }
            
    # def get_personne_profile_from_li(self, personne_li):
    #     personne_dic = {}
    #     a_profile_url = self.get_element('div/section/div/div/div[2]/div[1]/a[@class="app-aware-link  link-without-visited-state"]', from_elem=personne_li)
    #     if a_profile_url["status"]:
    #         a_profile_url = a_profile_url["data"]
    #         personne_dic['profile_url'] = a_profile_url.get_attribute('href')
    #         personne_dic['person_name'] = a_profile_url.get_attribute("innerText")
    #     else:
    #         return {"status": False, "data": a_profile_url["data"] }

    #     div_profile_description = self.get_element('div/section/div/div/div[2]/div[@class="artdeco-entity-lockup__subtitle ember-view"]', from_elem=personne_li)
    #     if div_profile_description["status"]:
    #         div_profile_description = div_profile_description["data"]
    #         personne_dic['profile_description'] = div_profile_description.get_attribute("innerText")
            
    #     else:
    #         print({"status": False, "data": div_profile_description["data"] })
            
    #     return {"status": True, "data": personne_dic }

    # ########################################################################################################

    # def send_connection_invitation_from_profile_url(self, profile_url):
    #     pass
        
    # def extract_urls_from_linkedin_profiles_in_my_network(self):
    #     pass
    
    # def extract_urls_from_linkedin_profiles_in_sales_navigator(self, filter_dic):
    #     pass
    
    # def extract_posts_from_linkedin_profile_url(self, profile_url):
    #     pass
        
    # def check_if_a_linkedin_profile_is_open_inmail_or_not(selfx, profile_url):
    #     pass
        
    # def send_message_to_LinkedIn_profile_open_inmail(self, message, profile_url):
    #     pass
    