from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time , random
import os, re, json, copy
import zipfile
from bs4 import BeautifulSoup

from Item import EditeurLogiciels
from ItemStorage import ItemStorage

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

    def scroll_down(self, button_path_to_show_more_results=None, button_text_to_show_more_results=None, bottom_distance=0):
        # bottom_distance => distance between the bottom of the page and the More results button
    
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        second_check = False
        while True:
            # Scroll down to bottom
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight  - {bottom_distance});")
            # Calculate new scroll height and compare with total scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            # Wait to load page
            time.sleep(random.uniform(4, 5))
            if new_height == last_height:
                
                temp = False
                if not temp:
                    if button_text_to_show_more_results in str(self.get_element('//body')['data'].get_attribute('innerText')).lower():
                        show_more_results_button = self.get_element(button_path_to_show_more_results, group=True, innerTextLower=button_text_to_show_more_results)
                        if show_more_results_button["status"]:
                            show_more_results_button = show_more_results_button["data"]
                            self.click_elem(show_more_results_button)
                            temp = True
                            print("yeeeees : 'show_more_results_button' is clecked.......")
                            # Wait to load page
                            time.sleep(random.uniform(4, 5))
                if second_check and not temp:
                    break
                    
                if not temp:
                    second_check = True
                time.sleep(random.uniform(1.5,2.5))

            last_height = new_height
    ########################################################################################################
    def extract_editeur_de_logiciels_from_cloudlist_from_article(self, article):
        dict = {}
        a_elem = self.get_element('div[2]/header/h2/a', from_elem=article)
        if a_elem['status']:
            a_elem = a_elem['data']
            dict['name'] = a_elem.get_attribute('innerText')
            dict['more_inf_url'] = a_elem.get_attribute('href')

        address_elem = self.get_element('div[2]/div[1]/span[2]/address/span/span[1]', from_elem=article)
        if address_elem['status']:
            address_elem = address_elem['data']
            dict['address'] = address_elem.get_attribute('innerText')

        tele_elem = self.get_element('div[2]/div[3]/span[2]/a', from_elem=article)
        if tele_elem['status']:
            tele_elem = tele_elem['data']
            dict['tele'] = tele_elem.get_attribute('innerText')
        
        return dict

    def extract_editeurs_de_logiciels_from_cloudlist(self, storage_file_path=None):

        editeurs_articles = self.get_element('//div[@class="w2dc-listings-block-content"]/article', group=True)
        if editeurs_articles['status'] :
            editeurs_articles = editeurs_articles['data']
            print(len(editeurs_articles))
            editeurs = []
            for i, article in enumerate(editeurs_articles):
                editeur_dict = self.extract_editeur_de_logiciels_from_cloudlist_from_article(article)
                editeur_dict['index'] = i
                editeur = EditeurLogiciels()
                editeur.init_from_dict(editeur_dict)
                editeurs.append(editeur)
            if storage_file_path:
                ItemStorage(file_path=storage_file_path, value=editeurs)
            return editeurs
        else:
            print(editeurs_articles['data'])
    ########################################################################################################
    def extract_more_info_for_editeurs_from_cloudlist(self, file_path='', storage_file_path='', storage_file_path_2=''):
        itemStorage = ItemStorage(file_path = file_path)
        editeurs_dict = itemStorage.get_list_of_dicts()
    
        editeurs = []
        info_names = []
        for editeur_dict in editeurs_dict:
            editeur = EditeurLogiciels()
            editeur.init_from_dict(editeur_dict)
            self.driver.get(editeur.more_inf_url)
            
            description = self.get_element('//div[@class="w2dc-field-content w2dc-field-description"]')
            if description['status']:
                description = description['data']
                editeur.description = description.get_attribute('innerText')
                
                print(description.get_attribute('innerText'))
            else:
                print(description['data'])
    
            infos = self.get_element('//div[@id="w2dc-fields-group-1"]/div', group=True)
            if infos['status']:
                infos = infos['data']
                for i, info in enumerate(infos):
                    if i>0:                        # le premier element contient juste le mot : COORDONNÉES
                        spans_info = self.get_element('span', group=True, from_elem=info)['data']
                        if len(spans_info) >= 2:
                            info_name = spans_info[0].get_attribute('innerText')
                            info_value = spans_info[1].get_attribute('innerText')
                            info_names.append(info_name)
                            
                            if str(info_name).lower().strip() == 'téléphone:':
                                if not editeur.tele or str(editeur.tele) == 'nan' :
                                    editeur.tele = [info_value.strip()]
                                else:
                                    if str(editeur.tele).strip() == info_value.strip():
                                        editeur.tele = [info_value.strip()]
                                    else:
                                        editeur.tele = [str(editeur.tele).strip(), info_value.strip()]
                                        
                            if str(info_name).lower().strip() == 'site web:':
                                editeur.web_site_url = info_value.strip()
                                
                            if str(info_name).lower().strip() == 'email:':
                                editeur.email = info_value.strip()
                                
                            print(f'{info_name} ==> {info_value}')
                        else:
                            print('no len(spans_info) >= 2')
            else:
                print(infos['data'])
    
            print(editeur.more_inf_url)
            print(f'*'*150)
    
            ItemStorage(file_path=storage_file_path, value=editeur)
            editeurs.append(editeur)
            time.sleep(1)
            
        ItemStorage(file_path=storage_file_path_2, value=editeurs)
        return list(set(info_names))
    ########################################################################################################
    def extract_editeur_de_logiciels_from_archimag_from_div(self, div_elem):
        dict = {}
        a_elem = self.get_element('div/div[2]/h2/a', from_elem=div_elem)
        if a_elem['status'] :
            a_elem = a_elem['data']
            dict['name'] = a_elem.get_attribute('innerText')
            dict['more_inf_url'] = a_elem.get_attribute('href')
        else:
            print(a_elem['data'])

    
        tags_elems = self.get_element('div/div[2]/ul[2]/li', from_elem=div_elem, group=True)
        if tags_elems['status'] :
            tags_elems = tags_elems['data']
            tags = [tag_elem.get_attribute('innerText') for tag_elem in tags_elems]
        else:
            print(tags_elems['data'])

        tags_elems = self.get_element('div/div[2]/ul[3]/li', from_elem=div_elem, group=True)
        if tags_elems['status'] :
            tags_elems = tags_elems['data']
            tags = tags + [tag_elem.get_attribute('innerText') for tag_elem in tags_elems]
            dict['tags'] = ',,  '.join(tags)
        else:
            print(tags_elems['data'])
            
        description_elem = self.get_element('div/div[2]', from_elem=div_elem)
        if description_elem['status'] :
            description_elem = description_elem['data']
            dict['description'] = description_elem.text
        else:
            print(description_elem['data'])
        
        return dict

    def extract_editeurs_de_logiciels_from_archimag(self, storage_file_path=None):
        editeurs_divs_1 = self.get_element('//*[@id="block-system-main"]/div/div/div[1]/div/div/div', group=True)
        editeurs = []
        if editeurs_divs_1['status'] :
            editeurs_divs_1 = editeurs_divs_1['data']
            print(len(editeurs_divs_1))
            for editeur_div_1 in editeurs_divs_1:
                editeur = EditeurLogiciels()
                dict = self.extract_editeur_de_logiciels_from_archimag_from_div(editeur_div_1)
                editeur.init_from_dict(dict)
                editeurs.append(editeur)
                print(editeur)
        else:
            print(editeurs_divs_1['data'])
            
        print(f'*'*150)
        editeurs_divs_2 = self.get_element('//*[@id="block-system-main"]/div/div/div[2]/div', group=True)
        if editeurs_divs_2['status'] :
            editeurs_divs_2 = editeurs_divs_2['data']
            print(len(editeurs_divs_2))
            for editeur_div_2 in editeurs_divs_2:
                editeur = EditeurLogiciels()
                dict = self.extract_editeur_de_logiciels_from_archimag_from_div(editeur_div_2)
                editeur.init_from_dict(dict)
                editeurs.append(editeur)
                print(editeur)
        else:
            print(editeurs_divs_2['data'])

        if storage_file_path:
            ItemStorage(file_path=storage_file_path, value=editeurs)
            
    ########################################################################################################
    def extract_more_info_for_editeurs_from_archimag(self, file_path='', storage_file_path='', storage_file_path_2=''):
        itemStorage = ItemStorage(file_path = file_path)
        editeurs_dict = itemStorage.get_list_of_dicts()
    
        editeurs = []
        info_names = []
        for i, editeur_dict in enumerate(editeurs_dict):
            editeur = EditeurLogiciels()
            editeur.init_from_dict(editeur_dict)
            editeur.index = i
            self.driver.get(editeur.more_inf_url)
            
            contact_elem = self.get_element('//article[@class="node node-societe"]/div[2]/div[1]/div/div[3]/div[1]')
            if contact_elem['status']:
                contact_elem = contact_elem['data']
                editeur.contact = contact_elem.get_attribute('innerText')
            else:
                print(contact_elem['data'])

            contact_commercial_elem = self.get_element('//article[@class="node node-societe"]/div[2]/div[1]/div/div[3]/div[2]')
            if contact_commercial_elem['status']:
                contact_commercial_elem = contact_commercial_elem['data']
                editeur.commercial_name = contact_commercial_elem.get_attribute('innerText')
            else:
                print(contact_commercial_elem['data'])

            nos_domaines_elem = self.get_element('//article[@class="node node-societe"]/div[2]/div[1]/div/div[3]/div[3]')
            if nos_domaines_elem['status']:
                nos_domaines_elem = nos_domaines_elem['data']
                editeur.nos_domaines = nos_domaines_elem.get_attribute('innerText')
            else:
                print(nos_domaines_elem['data'])
            
            description_elem = self.get_element('//article[@class="node node-societe"]/div[2]/div[1]/div/div[2]/div[2]/div/div/div')
            if description_elem['status']:
                description_elem = description_elem['data']
                editeur.description = description_elem.get_attribute('innerText')
            else:
                print(nos_domaines_elem['data'])
                
            print(editeur.contact)
            print(f'*'*20)
            print(editeur.commercial_name)
            print(f'*'*20)
            print(editeur.nos_domaines)
            print(f'*'*20)
            print(editeur.description)
            print(f'*'*20)
            print(editeur.more_inf_url)
            print(f'*'*150)
            
            if storage_file_path:
                ItemStorage(file_path=storage_file_path, value=editeur)
                editeurs.append(editeur)
                time.sleep(1)
        if storage_file_path_2 :
            ItemStorage(file_path=storage_file_path_2, value=editeurs)
            
        return list(set(info_names))
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
    