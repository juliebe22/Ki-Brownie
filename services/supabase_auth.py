from supabase import create_client
from config import Config


def criar_cliente_supabase():
    if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
        raise RuntimeError(
            "Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env"
        )

    return create_client(
        Config.SUPABASE_URL,
        Config.SUPABASE_KEY
    )


def autenticar_admin(email, senha):
    cliente = criar_cliente_supabase()

    resposta = cliente.auth.sign_in_with_password({
        "email": email,
        "password": senha
    })

    if not resposta.user or not resposta.session:
        return None

    emails_autorizados = {
        email.strip().lower()
        for email in Config.ADMIN_EMAILS.split(",")
        if email.strip()
    }

    email_usuario = (resposta.user.email or "").strip().lower()

    if email_usuario not in emails_autorizados:
        return None

    return {
        "id": resposta.user.id,
        "email": resposta.user.email,
        "access_token": resposta.session.access_token,
        "refresh_token": resposta.session.refresh_token
    }

def obter_usuario(access_token):
    if not access_token:
        return None

    cliente = criar_cliente_supabase()

    try:
        resposta = cliente.auth.get_user(access_token)

        if not resposta.user:
            return None

        return {
            "id": resposta.user.id,
            "email": resposta.user.email
        }

    except Exception:
        return None