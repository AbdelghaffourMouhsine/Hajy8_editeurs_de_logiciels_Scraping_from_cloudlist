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

class LinkedinAutomation:
    
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
    #---------------------------------- get linkedin authentication ----------------------------------------
    ########################################################################################################
    def get_linkedin_authentication(self, email = '', pwd = ''):
        
        url = 'https://www.linkedin.com/login/fr?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
        self.driver.get(url)
        time.sleep(2)
        
        input_username = self.get_element('//*[@id="username"]')
        if input_username["status"]:
            input_username = input_username["data"]
            input_username.send_keys(email)
            input_username.send_keys(Keys.ENTER)
        else:
            print({"status": False, "data":input_username["data"] })
        time.sleep(2)

        input_password = self.get_element('//*[@id="password"]')
        if input_password["status"]:
            input_password = input_password["data"]
            input_password.send_keys(pwd)
            input_password.send_keys(Keys.ENTER)
        else:
            print({"status": False, "data":input_password["data"] })

        print('linkedin_authentication --> yes')
        time.sleep(20)
    ########################################################################################################
    #-------------------------------------------- scroll_down ----------------------------------------------
    ########################################################################################################
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
    #------- extract linkedin profiles that work at a company from the company linkedin profile url --------
    ########################################################################################################
    def extract_profiles_from_company_linkedin_profile_url(self, company_linkedin_url):
        company_linkedin_url = str(company_linkedin_url)
        time.sleep(random.uniform(1,1.5))
        
        try:
            if 'company' in company_linkedin_url :
            
                a_personnes_link = f'https://www.linkedin.com/company/{company_linkedin_url.split("/company/")[1].split("/")[0]}/people'
                                
                if a_personnes_link:
                    self.driver.get(a_personnes_link)
                    time.sleep(random.uniform(2,4.5))

                    self.scroll_down(button_path_to_show_more_results='//button', button_text_to_show_more_results='afficher plus de résultats')

                # /html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[2]/div/div/div[2]/div/div[1]/ul/li
                # //li[contains(@class,"org-people-profile-card__profile-card-spacing")]
                # //div[@class="artdeco-card org-people-profile-card__card-spacing org-people__card-margin-bottom"]/div/div/ul/li
                
                personnes_li_s = self.get_element('//li[contains(@class,"org-people-profile-card__profile-card-spacing")]', group=True)
                    
                profiles = []
                if personnes_li_s["status"]:
                    personnes_li_s = personnes_li_s["data"]
                    # print(f'le nombre de personnes avant extract est: {len(personnes_li_s)}')
                    for li in personnes_li_s:
                        profile = self.get_personne_profile_from_li(li)
                        if profile["status"]:
                            # print(profile["data"])
                            profiles.append(profile["data"])
                        # else:
                        #     print(f'profile : {profile}')
                    # print(f'le nombre de personnes apres extract est : {len(profiles)}')
                else:
                    print({"status": False, "data": personnes_li_s["data"] })
    
                return {"status": True, "data": profiles }

            else:
                return {"status": False, "data": 'not valid company_linkedin_url'}
                
        except Exception as e:
            print(f'ERROOOOR: ({company_linkedin_url},{type(company_linkedin_url)}) {e}')
            return {"status": False, "data": str(e) }

    #/div/section/div/div/div[2]/div[1]/a
    
    def get_personne_profile_from_li(self, personne_li):
        personne_dic = {}
        a_profile_url = self.get_element('div/section/div/div/div[2]/div[1]/a', from_elem=personne_li)
        if a_profile_url["status"]:
            a_profile_url = a_profile_url["data"]
            personne_dic['profile_url'] = a_profile_url.get_attribute('href')
            personne_dic['profile_name'] = a_profile_url.get_attribute("innerText")
        else:
            # print(personne_li.get_attribute('innerText'))
            return {"status": False, "data": a_profile_url["data"] }

        div_profile_description = self.get_element('div/section/div/div/div[2]/div[@class="artdeco-entity-lockup__subtitle ember-view"]', from_elem=personne_li)
        if div_profile_description["status"]:
            div_profile_description = div_profile_description["data"]
            personne_dic['profile_description'] = div_profile_description.get_attribute("innerText")
            
        else:
            print({"status": False, "data": div_profile_description["data"] })
            
        return {"status": True, "data": personne_dic }

    ########################################################################################################
    #------------------------- get company linkedin url from company web site url --------------------------
    ########################################################################################################
    def get_company_linkedin_url_from_company_web_site_url(self, company_web_site_url):
        company_web_site_url = str(company_web_site_url).strip()
        try:
            if company_web_site_url:
                self.driver.get(company_web_site_url)
                time.sleep(0.5)
                
                html_content = self.driver.page_source
                # Analyser le contenu HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Rechercher les liens LinkedIn dans les balises <a>
                linkedin_links = []
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    # Vérifier si l'URL contient 'linkedin.com'
                    if 'linkedin.com' in href and 'company' in href:
                        linkedin_links.append(href)
                
                # Afficher les liens LinkedIn extraits
                print(linkedin_links)
                
                company_linkedin_url = None
                if linkedin_links:
                    company_linkedin_url = linkedin_links[0]

                return {"status": True, "data": company_linkedin_url}
            else:
                return {"status": False, "data": None }
        except Exception as e:
            print(f'ERROOOR: {e}')
            return {"status": False, "data": str(e)}
            
    ############################################################################################################
    #----------------------------- linkedin url from GOOGLE based on company_name ------------------------------
    ############################################################################################################
    def get_google_page(self):
        self.driver.get('https://www.google.com')
        time.sleep(random.uniform(0.5, 2))
        
        input_search = self.get_element('//*[@id="APjFqb"]')
        if input_search["status"]:
            input_search = input_search["data"]
            input_search.send_keys('some keys for get results')
            input_search.send_keys(Keys.ENTER)
        else:
            print({"status": False, "data":input_search["data"] })
        time.sleep(3)
        
    def get_linkedin_url_from_company_name(self, company_name):
        company_name = str(company_name)
        try:
            input_search = self.get_element('//*[@id="APjFqb"]')
            if input_search["status"]:
                input_search = input_search["data"]
                # Effacer le champ de saisie avant d'ajouter une nouvelle valeur
                input_search.clear()  # Supprime le contenu existant de l'input
                keywords = company_name.strip() + ' linkedin company'
                input_search.send_keys(keywords)  # Ajouter la nouvelle valeur
                time.sleep(random.uniform(0.5, 2))
                input_search.send_keys(Keys.ENTER)  # Envoyer le formulaire ou valider la recherch
            else:
                print({"status": False, "data":input_search["data"] })
            time.sleep(random.uniform(1,1.5))
            
            a_linkedin = self.get_element('//a[@jsname="UWckNb"]')
            if a_linkedin["status"]:
                a_linkedin = a_linkedin["data"]
                linkedin_url = a_linkedin.get_attribute('href')
                return {"status": True, "data": linkedin_url }
                
            else:
                print({"status": False, "data": a_linkedin["data"] })
                return {"status": False, "data": a_linkedin["data"]}
            
        except Exception as e:
            print(f'ERROOOR: {e}')
            return {"status": False, "data": str(e) }

    ########################################################################################################
    ########################################################################################################
    
    ########################################################################################################
    ########################################################################################################
            
    def send_connection_invitation_from_profile_url(self, profile_url):
        pass
        
    def extract_urls_from_linkedin_profiles_in_my_network(self):
        pass
    
    def extract_urls_from_linkedin_profiles_in_sales_navigator(self, filter_dic):
        pass
    
    def extract_posts_from_linkedin_profile_url(self, profile_url):
        pass
        
    def check_if_a_linkedin_profile_is_open_inmail_or_not(selfx, profile_url):
        pass
        
    def send_message_to_LinkedIn_profile_open_inmail(self, message, profile_url):
        pass
    