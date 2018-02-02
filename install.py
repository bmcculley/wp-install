from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
import pymysql.cursors
import requests
import zipfile
import StringIO

# need to load settings from a config file
site_url = "http://wp.dev"
path_to_install = "/var/www/html"
wpdl = "https://wordpress.org/latest.zip"

# set the site details
site_name = "WPDev"
site_user = "username"
site_pass = "password"
confirm_pass = "" #checkbox value
site_email = "admin@example.com"
se_vis = "" #checkbox value
site_lang = "en_US"

# database settings
db_host = "localhost" 
db_admin = "root"
dba_pass = "password"

# give option to pull database name and user name
db_name = "wpdev"
db_user = "wp_user"
db_pass = "password"
db_prefix = "wp_"

def generate_random_username(length=8, chars=ascii_lowercase+digits):
    """ This function generates a random username.
    It defaults to a length of 8 characters.
    """
    return ''.join([choice(chars) for i in xrange(length)])

def gen_password(length=16, chars=ascii_lowercase+ascii_uppercase+digits):
    """ Generate a secure random password
    """
    chars = chars + "!@#$%^&*()"
    return ''.join([choice(chars) for i in xrange(length)])

# this function needs to accept more parameters
def create_database(db_host, db_admin, dba_pass, db_name, db_user, db_pass):
    # create the database connection
    conn = pymysql.connect(host=db_host,
                            user=db_admin,
                            password=dba_pass,
                            charset="utf8")

    try:
        with conn.cursor() as cursor:
            sql = "create database %s"% db_name
            cursor.execute(sql)
            sql = "create user '%s'@'localhost' identified by '%s'"% (db_user, db_pass)
            cursor.execute(sql)
            sql = "grant all privileges on %s . * to '%s'@'localhost'"% (db_name, db_user)
            cursor.execute(sql)
            sql = "flush privileges"
            cursor.execute(sql)

        conn.commit()
    finally:
        conn.close()

def download_unzip_wp(path_to_install):
    # download the latest wordpress and extract
    r = requests.get(wpdl, stream=True)
    z = zipfile.ZipFile(StringIO.StringIO(r.content))
    z.extractall(path=path_to_install)
    # we should check and set the permissions properly
    # looks like the best method would be using os stat
    # https://stackoverflow.com/a/16249655

def install_wp(site_url, site_name, site_user, site_pass, site_email):
    # use requests to install wp
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    # let's build the first POST 
    url_setup = site_url + "/wp-admin/setup-config.php?step=2"
    post_data = {
                    'dbname':db_name,
                    'uname':db_user,
                    'pwd':db_pass,
                    'dbhost':db_host,
                    'prefix':db_prefix,
                    'language':'',
                    'submit':'Submit'
                }
    r = session.post(url_setup, data=post_data)
    # check to make sure this returned ok
    if r.status_code == requests.codes.ok:
        # oops, we need to get request this url too
        url_install_1 = site_url + "/wp-admin/install.php?language=en_US"
        r = session.get(url_install_1)
        if r.status_code == requests.codes.ok:
            url_install = site_url + "/wp-admin/install.php?step=2"
            post_data = {
                            'weblog_title':site_name,
                            'user_name':site_user,
                            'admin_password':site_pass,
                            'pass1-text':site_pass,
                            'admin_password2':site_pass,
                            'pw_weak':'on',
                            'admin_email':site_email,
                            'Submit':'Install+WordPress',
                            'language':site_lang
                        }
            r = session.post(url_install, data=post_data)
            if r.status_code == requests.codes.ok:
                return "WordPress successfully installed."
    return "oh snap, something went wrong."


if __name__ == '__main__':
    print("creating the database")
    #create_database(db_host, db_admin, dba_pass, db_name, db_user, db_pass)
    print("done")
    print("downloading wordpress to the install directory")
    #download_unzip_wp(path_to_install)
    print("all set")
    print("let's install WordPress")
    print(install_wp(site_url, site_name, site_user, site_pass, site_email))