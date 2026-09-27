import os
import resend

from app.core.config import get_settings


class EmailService:

    def __init__(self):
        settings = get_settings()
        resend.api_key = settings.resend_api_key

    def send_reset_password_email(self, to_email: str, reset_token: str):
        reset_link = f"http://localhost:3000/redefinir_senha?token={reset_token}"

        params: resend.Emails.SendParams = {
            "from": "nao-responda@recuperacao.drisai.me",
            "to": [to_email],
            "subject": "Recuperação de Senha - DRISAI API",
            "html": f"""
                <h3>Recuperação de Senha</h3>
                <p>Você solicitou a alteração de senha. Clique no link abaixo para redefinir:</p>
                <a href="{reset_link}">Redefinir minha senha</a>
                <p><small>Este link expira em 15 minutos.</small></p>
            """,
        }

        resend.Emails.send(params)