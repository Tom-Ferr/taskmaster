import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


def send_alert(logfile, email, text):
    # Configurações do servidor de e-mail
    smtp_server = 'smtp.gmail.com'  # Exemplo: smtp.gmail.com
    smtp_port = 587  # Porta para TLS (geralmente 587)
    email_user = os.getenv('TASKMASTER_EMAIL')
    email_password = os.getenv('TASKMASTER_PASS')

    if not email_user or not email_password:
        print("ERROR: Unable to trigger email log alert as we did not find the 'TASKMASTER_EMAIL' and 'TASKMASTER_PASS' credentials in your environment")
        return

    # Criando a mensagem
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email
    msg['Subject'] = 'Taskmaster Log Alert'

    # Corpo do e-mail
    corpo_email = f'A record was generated in the Taskmaster server log file that we believe you should be aware of.\nThe record was as follows:\n\n    "{text}"\n\nThe log file is attached to help with the analysis.\nAtt.,\n\nTaskmaster Team'
    msg.attach(MIMEText(corpo_email, 'plain'))
    arquivo = logfile  # Caminho para o arquivo

    try:
        with open(arquivo, 'rb') as f:
            # Cria uma parte MIMEBase para o anexo
            parte = MIMEBase('application', 'octet-stream')
            parte.set_payload(f.read())
            encoders.encode_base64(parte)  # Codifica o arquivo em base64

            # Adiciona cabeçalhos
            parte.add_header('Content-Disposition', f'attachment; filename={os.path.basename(arquivo)}')

            # Anexa o arquivo à mensagem
            msg.attach(parte)

        # Conectando ao servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Iniciando criptografia TLS
        server.login(email_user, email_password)  # Autenticando no servidor
        server.sendmail(email_user, msg['To'], msg.as_string())  # Enviando o e-mail
        server.quit()  # Fechando a conexão
        print('INFO: Alert email sent successfully')
    except Exception as e:
        print(f'ERROR: Unable to send alert email: {e}')