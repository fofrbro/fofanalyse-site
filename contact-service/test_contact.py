"""Tests du formulaire de contact (sans réseau : SMTP simulé)."""

import pytest
from starlette.requests import Request

import contact


class FakeSMTP:
    sent = []

    def __init__(self, host, port, timeout=None):
        self.host, self.port = host, port

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def send_message(self, email):
        FakeSMTP.sent.append(email)


@pytest.fixture(autouse=True)
def smtp(monkeypatch):
    FakeSMTP.sent = []
    monkeypatch.setattr(contact.smtplib, "SMTP_SSL", FakeSMTP)
    monkeypatch.setattr(contact.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(contact, "limiter", contact.RateLimiter(per_ip_per_hour=2, per_day=3))
    for key, value in {
        "SMTP_HOST": "smtp.example.test", "SMTP_USER": "u", "SMTP_PASSWORD": "p",
        "CONTACT_FROM": "site@fofanalyse.com", "CONTACT_TO": "cheikhou@fofanalyse.com",
    }.items():
        monkeypatch.setenv(key, value)
    return FakeSMTP


def request(ip="203.0.113.7"):
    return Request({"type": "http", "headers": [(b"x-forwarded-for", ip.encode())], "client": ("10.0.0.2", 1)})


def post(ip="203.0.113.7", **fields):
    values = {
        "name": "Claire Martin", "email": "claire@banque.example", "company": "Banque du Nord",
        "message": "Bonjour, votre profil nous intéresse pour un poste de data engineer.",
        "lang": "fr", "website": "",
    }
    values.update(fields)
    return contact.contact(request(ip), **values)


def location(response):
    return response.status_code, response.headers["location"]


def test_valid_message_is_sent_with_reply_to_the_recruiter(smtp):
    assert location(post()) == (303, "/contact-envoye.html")

    email = smtp.sent[0]
    assert email["To"] == "cheikhou@fofanalyse.com"
    assert email["Reply-To"] == "Claire Martin <claire@banque.example>"
    assert email["Subject"] == "[fofanalyse.com] Message de Claire Martin"
    assert "Banque du Nord" in email.get_content()


def test_english_form_redirects_to_english_pages():
    assert location(post(lang="en")) == (303, "/en/contact-sent.html")
    assert location(post(lang="en", email="nope")) == (303, "/en/contact-error.html")


@pytest.mark.parametrize(
    "fields",
    [
        {"name": ""},
        {"email": "pas-une-adresse"},
        {"message": "court"},
        {"message": "x" * 5001},
        {"company": "x" * 121},
    ],
)
def test_invalid_forms_are_not_sent(smtp, fields):
    assert location(post(**fields)) == (303, "/contact-erreur.html")
    assert smtp.sent == []


def test_header_injection_is_neutralised(smtp):
    post(name="Claire\r\nBcc: victime@example.com")

    email = smtp.sent[0]
    assert email["Bcc"] is None
    assert "\n" not in email["Subject"]


def test_honeypot_pretends_success_without_sending(smtp):
    assert location(post(website="http://spam.example")) == (303, "/contact-envoye.html")
    assert smtp.sent == []


def test_rate_limit_per_ip_and_per_day(smtp):
    assert location(post())[1] == "/contact-envoye.html"
    assert location(post())[1] == "/contact-envoye.html"
    assert location(post())[1] == "/contact-erreur.html"  # 3e message de la même IP
    assert location(post(ip="198.51.100.9"))[1] == "/contact-envoye.html"
    assert location(post(ip="192.0.2.44"))[1] == "/contact-erreur.html"  # plafond du jour
    assert len(smtp.sent) == 3


def test_ip_window_slides_after_an_hour():
    now = [0.0]
    limiter = contact.RateLimiter(per_ip_per_hour=1, per_day=10, clock=lambda: now[0])

    assert limiter.allow("a")
    assert not limiter.allow("a")
    now[0] = 3601
    assert limiter.allow("a")


def test_smtp_failure_shows_the_error_page(monkeypatch):
    def broken(*args, **kwargs):
        raise OSError("connexion refusée")

    monkeypatch.setattr(contact.smtplib, "SMTP_SSL", broken)

    assert location(post()) == (303, "/contact-erreur.html")


def test_missing_configuration_shows_the_error_page(monkeypatch):
    monkeypatch.delenv("SMTP_HOST")

    assert location(post()) == (303, "/contact-erreur.html")


def test_starttls_mode(smtp, monkeypatch):
    monkeypatch.setenv("SMTP_SECURITY", "starttls")
    monkeypatch.setenv("SMTP_PORT", "587")

    assert location(post())[1] == "/contact-envoye.html"
    assert len(smtp.sent) == 1
