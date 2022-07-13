from selenium import webdriver	
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import sys
import os
from apufunktiot import *
import time 

# Firewall IPs
default_IP = "https://192.168.2.200"
service_IP = "https://192.168.200.1"

# Firmware versions
current_firmware_version = "4.32.2"
current_bootloader_version = "2017.12.0-8"

# Get resource path
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


# Current users Downloads folder path
downloads_path = str(Path.home() / "Downloads")
# Firmware update file path: "Current working directory + \Update file name"
firmware_file_path = resource_path('WeOS-' + current_firmware_version + '.pkg')


#Webdriver options and preferences
options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')
options.add_argument('--safebrowsing-disable-download-protection')
options.add_argument('safebrowsing-disable-extension-blacklist')
options.add_argument('log-level=3')     ## removes unnecessary logging to CMD
options.add_experimental_option('excludeSwitches', ['enable-logging'])  ## removes DevTool messages to CMD
prefs = {
  "download.default_directory": downloads_path,
  "download.prompt_for_download": False,
  "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)
# Run Chrome headless
options.headless = True
# sleep time after FW upgrade
sleep_time = 35     

# Create a chromedriver instance
driver = webdriver.Chrome(executable_path=resource_path('./driver/chromedriver.exe'), options=options)
driver.implicitly_wait(10)

def main():
      
  print("\n##### WESTERMO FW AUTOMATION #####\n")
  # Ask if firewall configuration should be restored
  upload_config = y_or_n('Restore firewall configuration file after firmware upgrade?')

  if upload_config:
    # User input for path to Firewall config file 
    print("\nTo enter firewall config path, shift + right click the config file, select \"Copy As path\" and paste into westermo-fw-automation.exe window.")
    config_path = raw(input("Enter firewall config file path: ")).replace('"', '').lstrip('\\').rstrip('\\')

    #check if file exists
    if not os.path.isfile(config_path):
      print("Config file not found")
      print('Exiting appplication in 5 seconds')
      time.sleep(5)
      sys.exit()
    #print(config_path)     # FOR DEBUGGING PATHS
    #time.sleep(10)         # FOR DEBUGGING PATHS

    # User input for Firewall password
    fw_password = raw(input("Enter password for firewall (leave blank for default password): "))
    change_password = False if fw_password == '' else True
    # Ask if configuration backup file should be downloaded

    backup_download = y_or_n("Download config backup file?")
    if backup_download == True:
      print('Config backup will be downloaded to ' + downloads_path)


  while True:
    try:
          # Login to Westermo default address with default credentials
        print("Connecting to " + default_IP + "...")
        driver.get(default_IP)
        
    except:
        try: 
            # If default IP doesn't work login to Westermo Wärstilä Service IP
            # address with default credentials
            print("Trying with Wärtsilä service IP...")
            driver.get(service_IP)
        except:
            print('Could not connect to WeOS, check connection.')
            print("Exiting application.")
            driver.quit_driver()
            sys.exit()
        else:
          # Set target IP to Wärtsilä service IP
          target_ip = service_IP
          break
      
    else:
      # Set target IP to Westermo default IP
      target_ip = default_IP
      break
  
  print("Connected to " + target_ip)

  # Find texbox for username and enter information
  user = driver.find_element(By.ID, "uname").send_keys('admin')
  # Find texbox for password, enter password and login
  password = driver.find_element(By.ID, "pass").send_keys('westermo' + Keys.ENTER)
  
  # Check firmware versions
  driver.find_element(By.XPATH, "//*[@id='menu_status']").click()  # Status menu
  driver.find_element(By.XPATH, "//*[@id='menu_system_details']").click()
  time.sleep(1)
  primary_version = driver.find_element(By.XPATH, "//*[@id='value_fw_ver']").text
  backup_version = driver.find_element(By.XPATH, "//*[@id='value_bkp_fw_ver']").text
  bootloader_version = driver.find_element(By.XPATH, "//*[@id='value_bootload_ver']").text
  #driver.find_element(By.XPATH, "//*[@id='menu_status']").click()  # Back to status menu
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='menu_status']"))).click()
  
  print("\nPrimary firmare:\t" + primary_version)
  print("Backup firmaware:\t" + backup_version)
  print("Bootloader version:\t" + bootloader_version)
  print("")
  

  ##################################### 
  ##      BOOT FIRMWARE UPGRADE      ##
  #####################################
  if bootloader_version != current_bootloader_version:
    # Navigate to maintenance menu
    maintenance = driver.find_element(By.ID, "menu_maintenance").click()
    # Navigate to maintenance menu
    firmware = driver.find_element(By.ID, "menu_firmware").click()
    # Enable uploading of firmware file
    enableupload = driver.find_element(By.XPATH, "//*[@id='content']/form[1]/a").click()
    # Choose file to upload via Windows menu
    choosefile = driver.find_element(By.XPATH, "//*[@id='fw_file']").send_keys(firmware_file_path)
    # Select option/image
    #imageupgrade = driver.find_element(By.NAME, "target_image").click()

    # Select option/image
    drop = Select(driver.find_element(By.NAME, "target_image"))
    drop.select_by_index(2)     ## select BOOT

    # Apply upgrade
    print("Upgrading boot firmware...")
    enableupload = driver.find_element(By.NAME, "apply").click()
    # Wait until the upgrade is ready
    print("Waiting for ", sleep_time, " seconds")
    time.sleep(sleep_time)
    print("Boot firmware upgrade complete")

  ########################################
  ##      PRIMARY FIRMWARE UPGRADE      ##
  #######################################3
  if primary_version != current_firmware_version:
    try:
      driver.get(target_ip)
    except:
      print("Could not connect to " + target_ip + " , check network interface IP")
      print("Exiting application")
      sys.exit()

    # Find texbox for username and enter information
    user = driver.find_element(By.ID, "uname").send_keys('admin')
    # Find texbox for password, enter password and login
    password = driver.find_element(By.ID, "pass").send_keys('westermo' + Keys.ENTER)
    # Navigate to maintenance menu
    maintenance = driver.find_element(By.ID, "menu_maintenance").click()
    # Navigate to maintenance menu
    firmware = driver.find_element(By.ID, "menu_firmware").click()
    # Enable uploading of firmware file
    enableupload = driver.find_element(By.XPATH, "//*[@id='content']/form[1]/a").click()
    # Choose file to upload via Windows menu
    choosefile = driver.find_element(By.XPATH, "//*[@id='fw_file']").send_keys(firmware_file_path)
    # Select option/image
    #imageupgrade = driver.find_element(By.NAME, "target_image").click()
    # Select option/image
    drop = Select(driver.find_element(By.NAME, "target_image"))
    drop.select_by_index(0)     ## select PRIMARY

    # Apply upgrade
    print("Upgrading primary firmware...")
    enableupload = driver.find_element(By.NAME, "apply").click()
    # Wait until the upgrade is ready
    print("Waiting for", sleep_time, " seconds")
    time.sleep(sleep_time)
    print("Primary firmware upgrade complete")

  ######################################
  ##      BACKUP FIRMWARE UPGRADE     ##
  ######################################
  if backup_version != current_firmware_version:
    try:
      driver.get(target_ip)
    except:
      print("Could not connect to " + target_ip + " , check network interface IP")
      print("Exiting application")
      sys.exit()
    # Find texbox for username and enter information
    user = driver.find_element(By.ID, "uname").send_keys('admin')
    # Find texbox for password, enter password and login
    password = driver.find_element(By.ID, "pass").send_keys('westermo' + Keys.ENTER)
    # Navigate to maintenance menu
    maintenance = driver.find_element(By.ID, "menu_maintenance").click()
    # Navigate to maintenance menu
    firmware = driver.find_element(By.ID, "menu_firmware").click()
    time.sleep(1)
    # Enable uploading of firmware file
    enableupload = driver.find_element(By.XPATH, "//*[@id='content']/form[1]/a").click()
    # Choose file to upload via Windows menu
    choosefile = driver.find_element(By.XPATH, "//*[@id='fw_file']").send_keys(firmware_file_path)
    # Select option/image
    drop = Select(driver.find_element(By.NAME, "target_image"))
    drop.select_by_index(1)     ## select BACKUP
    print("Upgrading backup firmware...")

    # Apply upgrade
    enableupload = driver.find_element(By.NAME, "apply").click()
    # Wait until the upgrade is ready
    print("Waiting for", sleep_time, " seconds")
    time.sleep(sleep_time)
    driver.get(target_ip)
    print("Backup firmware upgrade complete")

  # If config upload chosen
  if upload_config:
    try:
      driver.get(target_ip)
    except:
      print("Could not connect to " + target_ip + " , check network interface IP")
      print("Exiting application")
      sys.exit()
    ##############################
    ##    CONFIG FILE UPLOAD    ##
    ##############################
    # Find texbox for username and enter information
    user = driver.find_element(By.ID, "uname").send_keys('admin')
    # Find texbox for password, enter password and login
    password = driver.find_element(By.ID, "pass").send_keys('westermo' + Keys.ENTER)
    # Navigate to maintenance menu
    maintenance = driver.find_element(By.ID, "menu_maintenance").click()
    # Choose file to upload via Windows explorer
    config_upload = driver.find_element(By.XPATH, "//*[@id='content']/form[2]/input[5]").send_keys(config_path)
    # Upload FW config file 
    print("Uploading FW config file...")
    config_restore = driver.find_element(By.XPATH, "//*[@id='content']/form[2]/input[6]").click()
    # Wait for config to apply
    print("Please wait")
    time.sleep(15)
    print("FW config file uploaded")

    ## PW change and backup download
    if change_password or backup_download:
      driver.get('https://192.168.200.1/')
      time.sleep(5)
      print("Connected to https://192.168.200.1")
      # Find texbox for username and enter information
      time.sleep(1)
      user = driver.find_element(By.ID, "uname").send_keys('admin')
      # Find texbox for password, enter password and login
      password = driver.find_element(By.ID, "pass").send_keys('westermo' + Keys.ENTER)
      # Navigate to maintenance menu
      maintenance = driver.find_element(By.ID, "menu_maintenance").click()

      if change_password:
        # Navigate to password menu
        maintenance = driver.find_element(By.ID, "menu_password").click()
        # Find texbox for FW password and enter it twice
        print("Changing FW password")
        fw_password_1 = driver.find_element(By.ID, "password").send_keys(fw_password)
        time.sleep(1)
        fw_password_2 = driver.find_element(By.ID, "password2").send_keys(fw_password)

        # Apply FW password
        apply_password = driver.find_element(By.NAME, "apply").click()
        print("Password changed")
      
      if backup_download:
        # Navigate to Backup & Restore menu
        print("Downloading backup...")
        maintenance = driver.find_element(By.ID, "menu_backup").click()

        # Download backup
        download_backup = driver.find_element(By.XPATH, "//*[@id='form_backup']/input[5]").click()

        print("Config backup downloaded to ", downloads_path)
    


while True:
  main()
  if not y_or_n("\nScript complete. Run script again?"):
        break
  else:
        continue
  
# Exit application
print("Exiting application.")
# Close chromedriver
driver.quit()



