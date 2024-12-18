import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurações do servidor SMTP
SMTP_SERVER = "imap.gmail.com"  # Substitua pelo servidor SMTP do seu provedor
SMTP_PORT = 993
SMTP_USER = "pix.stanux@gmail.com"  # Seu endereço de e-mail
SMTP_PASSWORD = "Lcstanux@2021*"       # Sua senha ou app password

# Configuração do e-mail
sender = SMTP_USER
recipient = "matheus_pavan@hotmail.com"
reply_to = "matheusi_marreco@hotmail.com"
subject = "Assunto do E-mail"
body = "Bike Depay! Ta louco!."
# IMAP_HOST=imap.hostinger.com.br
# IMAP_PORT=993
# IMAP_ENCRYPTION=ssl
# IMAP_VALIDATE_CERT=true
# IMAP_USERNAME=vinicius@stanux.com.br
# IMAP_PASSWORD=Vas070902
# IMAP_DEFAULT_ACCOUNT=default
# IMAP_PROTOCOL=imap
# Criação da mensagem
msg = MIMEMultipart()
msg["From"] = sender
msg["To"] = recipient
msg["Subject"] = subject
msg["Reply-To"] = reply_to

# Corpo do e-mail
msg.attach(MIMEText(body, "plain"))

# Enviando o e-mail
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Conexão segura
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(sender, recipient, msg.as_string())
    print("E-mail enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar o e-mail: {e}")
