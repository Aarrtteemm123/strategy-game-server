from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
class SystemService:
    def update_system(self):
        pass

    def send_email(self,from_email, to_email, password, message, title):
        msg = MIMEMultipart()  # create msg object
        msg['Subject'] = title  # title
        msg.attach(MIMEText(message, 'html'))  # attach text to msg as html
        server = smtplib.SMTP('smtp.gmail.com: 587')  # create server
        server.starttls()  # always use TLS protocol
        server.login(from_email, password)  # login
        server.sendmail(from_email, to_email, msg.as_string())  # send msg
        server.quit()  # destroy connection

    def get_feedback(self,username,user_email,rating,msg):
        msg_html = EmailTemplate().get_html_feedback(username,msg,user_email,rating)
        self.send_email('***@gmail.com','***@gmail.com','***',
                        msg_html,EmailTemplate.FEEDBACK_TITLE)

class EmailTemplate:

    REGISTRATION_TITLE = 'Register in strategy - Your country'
    DELETE_TITLE = 'Delete account in strategy - Your country'
    CHANGE_TITLE = 'Account data was changed in strategy - Your country'
    FEEDBACK_TITLE = 'New feedback from strategy - Your country'

    def get_html_registration(self,username,password,country_name,user_id,flag_link):
        html = """<html><body><h1 style="font-weight: bolder">
        Dear """+username+"""
        <p>Welcome to online strategy - 'Your country'</h1>
        <hr><p><h2 style="color:green">Account was registered successfully:</h2>
        <h3>Player data:</h3>
        <p>ID: """+user_id+"""
        <p>Login: """+username+"""
        <p>Password: """+password+"""
        <p>Country: """+country_name+"""
        <p>Flag: """ + flag_link + """
        <p><a href="http://htmlbook.ru/html/a/href">Click on this link and start play now!</a>
        <p><strong style="color:orange">If you have any question or problems, write on this email testtset1009@gmail.com</strong>
        </body></html>"""
        return html

    def get_html_delete_account(self,username):
        html = """<html><body><h1 style="font-weight: bolder">
        """+username+"""!
        <hr><p><h2 style="color:red">Your account was deleted</h2>
        <p><strong style="color:orange">If you have any question or problems, write on this email testtset1009@gmail.com</strong>
        </body></html>"""
        return html

    def get_html_edit_account(self,username,password,country_name,flag_link):
        html = """<html><body><h1 style="font-weight: bolder">
                """ + username + """ attention!
                <hr><p><h2 style="color:red">Account data was changed:</h2>
                <h3>New player data:</h3>
                <p>Username: """ + username + """
                <p>Password: """ + password + """
                <p>Country: """ + country_name + """
                <p>Flag: """ + flag_link + """
                <p><a href="http://htmlbook.ru/html/a/href">Click on this link and start play now!</a>
                <p><strong style="color:orange">If you have any question or problems, write on this email testtset1009@gmail.com</strong>
                </body></html>"""
        return html

    def get_html_feedback(self,username,msg,player_email,rating):
        html = """<html><body><h1 style="font-weight: bolder">
                        Player """ + username + """ write feedback!</h1><hr>
                        <h3>Message:</h3>
                        <p>Rating: """ + rating + """/6
                        <p>""" + msg + """
                        <p><strong>Player email """+player_email+"""</strong>
                        </body></html>"""
        return html
