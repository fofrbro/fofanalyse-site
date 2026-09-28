"""
Service du formulaire de contact de fofanalyse.com.

Reçoit le formulaire (sans JavaScript), le vérifie et l'envoie par SMTP
dans la boîte du propriétaire du site, avec « Répondre à » sur l'adresse
du visiteur. Aucun message n'est conservé.

Protections :
- champ piège (« website ») invisible pour un humain : s'il est rempli,
  l'envoi est ignoré, mais le robot voit la page de remerciement ;
- limites : quelques messages par adresse IP et par heure, un plafond par
  jour pour tout le site ;
- champs bornés et nettoyés : aucun retour à la ligne dans les en-têtes
  de l'e-mail (injection d'en-têtes impossible).

Configuration par variables d'environnement : SMTP_HOST, SMTP_PORT,
SMTP_USER, SMTP_PASSWORD, SMTP_SECURITY (ssl ou starttls), CONTACT_TO,
CONTACT_FROM, CONTACT_PER_IP_PER_HOUR, CONTACT_PER_DAY.
"""

import os
import re
import smtplib
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LIMITS = {"name": 100, "email": 200, "company": 120, "message": 5000}
MIN_MESSAGE = 10

PAGES = {
    "fr": {"sent": "/contact-envoye.html", "error": "/contact-erreur.html"},
    "en": {"sent": "/en/contact-sent.html", "error": "/en/contact-error.html"},
}


@dataclass
class ContactMessage:
    name: str
    email: str
    company: str
    message: str
    lang: str


class InvalidMessage(ValueError):
    """Formulaire incomplet ou invalide."""


def _single_line(value: str) -> str:
    """Pas de retour à la ligne : protège les en-têtes de l'e-mail."""

    return re.sub(r"[\r\n\t]+", " ", value or "").strip()


def validate(name, email, company, message, lang) -> ContactMessage:
    name = _single_line(name)
    email = _single_line(email)
    company = _single_line(company)
    message = (message or "").strip()
    lang = lang if lang in PAGES else "fr"

    if not name or len(name) > LIMITS["name"]:
        raise InvalidMessage("nom manquant ou trop long")

    if not EMAIL_PATTERN.match(email) or len(email) > LIMITS["email"]:
        raise InvalidMessage("adresse e-mail invalide")

    if len(company) > LIMITS["company"]:
        raise InvalidMessage("entreprise trop longue")

    if not MIN_MESSAGE <= len(message) <= LIMITS["message"]:
        raise InvalidMessage("message trop court ou trop long")

    return ContactMessage(name, email, company, message, lang)


class RateLimiter:
    """Messages par adresse IP sur une heure glissante, et plafond du jour."""

    def __init__(self, per_ip_per_hour: int, per_day: int, clock=time.time):
        self.per_ip_per_hour = per_ip_per_hour
        self.per_day = per_day
        self._clock = clock
        self._by_ip: dict[str, deque] = defaultdict(deque)
        self._day: tuple[int, int] = (0, 0)  # (jour, messages)

    def allow(self, ip: str) -> bool:
        now = self._clock()
        recent = self._by_ip[ip]

        while recent and now - recent[0] > 3600:
            recent.popleft()

        day = int(now // 86400)
        today = self._day[1] if self._day[0] == day else 0

        if len(recent) >= self.per_ip_per_hour or today >= self.per_day:
            return False

        recent.append(now)
        self._day = (day, today + 1)
        return True


def build_email(message: ContactMessage, sender: str, recipient: str) -> EmailMessage:
    email = EmailMessage()
    email["Subject"] = f"[fofanalyse.com] Message de {message.name}"
    email["From"] = formataddr(("fofanalyse.com", sender))
    email["To"] = recipient
    email["Reply-To"] = formataddr((message.name, message.email))
    email.set_content(
        f"Nom : {message.name}\n"
        f"E-mail : {message.email}\n"
        f"Entreprise : {message.company or '-'}\n"
        f"Langue du site : {message.lang}\n\n"
        f"{message.message}\n"
    )
    return email


def send_email(email: EmailMessage) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.getenv("SMTP_PORT", "465"))
    user, password = os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"]

    if os.getenv("SMTP_SECURITY", "ssl") == "ssl":
        with smtplib.SMTP_SSL(host, port, timeout=15) as smtp:
            smtp.login(user, password)
            smtp.send_message(email)
    else:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(email)


app = FastAPI(title="fofanalyse.com contact", docs_url=None, redoc_url=None, openapi_url=None)
limiter = RateLimiter(
    per_ip_per_hour=int(os.getenv("CONTACT_PER_IP_PER_HOUR", "3")),
    per_day=int(os.getenv("CONTACT_PER_DAY", "50")),
)


def client_ip(request: Request) -> str:
    """Adresse du visiteur ; derrière Caddy, la première de X-Forwarded-For."""

    forwarded = request.headers.get("x-forwarded-for", "")
    return forwarded.split(",")[0].strip() or (request.client.host if request.client else "?")


@app.post("/api/contact")
def contact(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    company: str = Form(""),
    message: str = Form(""),
    lang: str = Form("fr"),
    website: str = Form(""),
):
    pages = PAGES.get(lang, PAGES["fr"])

    # Robot : faire comme si le message était parti.
    if website:
        return RedirectResponse(pages["sent"], status_code=303)

    try:
        checked = validate(name, email, company, message, lang)
    except InvalidMessage:
        return RedirectResponse(pages["error"], status_code=303)

    if not limiter.allow(client_ip(request)):
        return RedirectResponse(pages["error"], status_code=303)

    try:
        send_email(build_email(checked, os.environ["CONTACT_FROM"], os.environ["CONTACT_TO"]))
    except (KeyError, OSError, smtplib.SMTPException):
        return RedirectResponse(pages["error"], status_code=303)

    return RedirectResponse(pages["sent"], status_code=303)


@app.get("/api/contact/health")
def health():
    return {"status": "ok"}
