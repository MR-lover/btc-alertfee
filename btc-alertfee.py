from email.mime.text import MIMEText
from logging import getLogger, Formatter
from logging.handlers import RotatingFileHandler
from time import sleep
from urllib2 import Request, urlopen
import json
import smtplib

#### CHANGE VALUE BELOW ####
# Field "To" in the email header
email_to = "<TARGET EMAIL>"

# SMTP Host
email_host = "<EMAIL HOST>"
email_port = 25

# Username and password to login
email_user = "<EMAIL USERNAME TO LOGIN>"
email_pwd = "<EMAIL PASSWORD TO LOGIN>"

# Fee target (in satoshi)
fee_target = 250

# Period to check the fee (in seconds)
check_period = 300
#### DON'T TOUCH BELOW ####

class CustomLogger:
    def __init__(self, filepath, maxbytes=10000000, rotateN=5,
                 debuglevel=10, namelogger=None):
        self.log = getLogger(namelogger)
        try:
            log_format = Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s')
            log_handler = RotatingFileHandler(filepath, maxBytes=maxbytes,
                                              backupCount=rotateN)
            log_handler.setLevel(debuglevel)
            log_handler.setFormatter(log_format)
            self.log.addHandler(log_handler)
            self.log.setLevel(debuglevel)
        except Exception, e:
            print "[Logger] Error: %s" % e

    def debug(self, msg):
        self.log.debug(msg)

    def info(self, msg):
        self.log.info(msg)

    def warning(self, msg):
        self.log.warning(msg)

    def error(self, msg):
        self.log.error(msg)

    def critical(self, msg):
        self.log.critical(msg)


class BtcAlertFee:
    def __init__(self, email_to, email_user, email_pwd,
                 email_host, fee_target, check_period, email_port):
        self.settings = {
            "email": {
                "host": email_host,
                "port": email_port,
                "from": email_user,
                "to": email_to,
                "user": email_user,
                "pwd": email_pwd
            },
            "fee_target": fee_target,
            "check_period": check_period,
            "url": "https://bitcoinfees.21.co/api/v1/fees/recommended"
        }
        self.log = CustomLogger(filepath="global.log")
        self.log.info("=== [ Start ] ===")

    def getpage(self, url, retry_num=1, max_retry=3):
        ''' Get the page from url given '''
        if retry_num <= max_retry:
            try:
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                page = urlopen(req)
                if page.getcode() == 200:
                    return {"error": 0, "page": json.loads(page.read())}
                else:
                    self.log.error("Error when receive the page (RC: %s),"
                                   "retry" % page.getcode())
                    retry_num += 1
                    sleep(5)
                    return self.getpage(url=url, retry_num=retry_num)
            except Exception, e:
                self.log.error("Error when receive the page, retry")
                retry_num += 1
                sleep(5)
                return self.getpage(url=url, retry_num=retry_num)
        else:
            self.log.error("Max retry reach, skipping.")
            return {"error": 1}

    def sendmail(self, touser, fromuser, user, pwd, host, port, subject, msg):
        ''' Send alert message via mail '''
        email = MIMEText(msg)
        email["Subject"] = subject
        email["From"] = fromuser
        email["To"] = touser
        try:
            s = smtplib.SMTP(host=host, port=port)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(user=user, password=pwd)
            s.sendmail(from_addr=fromuser, to_addrs=touser,
                       msg=email.as_string())
            s.quit()
            return 0
        except Exception, e:
            self.log.error("Error during send, ERROR: ' %s '" % e)
            return 1

    def main(self):
        ''' Main Function '''
        page = self.getpage(url=self.settings["url"])
        if not page["error"]:
            current_fee = page["page"]["fastestFee"]
            msg = ("Current Fee: %s\nTarget Fee: %s\n\n\n"
                   "Github: https://github.com/Mirio/btc-alertfee\n"
                   "Donate (btc): 3JPRaDFPjjdR1Y7gBrdkfutbJ8g5X9GQik" % (
                       current_fee,  self.settings["fee_target"]))
            self.log.info("Current Fee: %s / Target: %s" % (
                current_fee, self.settings["fee_target"]))
            if current_fee <= self.settings["fee_target"]:
                sendmail = self.sendmail(
                    touser=self.settings["email"]["to"],
                    fromuser=self.settings["email"]["from"],
                    user=self.settings["email"]["user"],
                    pwd=self.settings["email"]["pwd"],
                    host=self.settings["email"]["host"],
                    port=self.settings["email"]["port"],
                    subject="[ALERT] Btc Transaction Fee",
                    msg=msg)
                if not sendmail:
                    self.log.info("Mail sent.")
                else:
                    self.log.error("Mail Error, check logs.")
            else:
                self.log.info("Nothing to do.")
            sleep(self.settings["check_period"])
            return self.main()
        else:
            self.log.error("Max retry reach, waiting 60s.")
            sleep(60)
            return self.main()


if __name__ == '__main__':
    try:
        obj = BtcAlertFee(email_to=email_to, email_user=email_user,
                          email_pwd=email_pwd, email_host=email_host,
                          email_port=email_port, fee_target=fee_target,
                          check_period=check_period)
        obj.main()
    except KeyboardInterrupt:
        print "Killed."
