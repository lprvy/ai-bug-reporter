import pytest

from bugreporter import heuristic
from bugreporter.models import Severity

NOTES = """Checkout crashes when applying coupon
1. log in as test user
2. add 2 items to cart
3. go to checkout and enter coupon SAVE10
expected: discount applied
actual: white screen, console shows TypeError
Chrome 131 on Windows 11, app version 2.4.1
"""


def test_extracts_full_report():
    r = heuristic.extract(NOTES)
    assert r.title == "Checkout crashes when applying coupon"
    assert r.severity is Severity.high
    assert r.component == "checkout"
    assert r.steps_to_reproduce == [
        "log in as test user",
        "add 2 items to cart",
        "go to checkout and enter coupon SAVE10",
    ]
    assert r.expected == "discount applied"
    assert r.actual == "white screen, console shows TypeError"
    assert r.environment.browser == "Chrome 131"
    assert r.environment.os == "Windows 11"
    assert r.environment.app_version == "2.4.1"
    assert {"auth", "crash", "payment"} <= set(r.labels)
    assert r.missing_info == []


@pytest.mark.parametrize(
    ("notes", "severity"),
    [
        ("Users were charged twice for one order", Severity.critical),
        ("Password reset email leaks other users' addresses", Severity.critical),
        ("Typo on pricing page: Montly", Severity.low),
        ("Avatar slightly misaligned on profile page", Severity.low),
        ("Search results load in the wrong order", Severity.medium),
    ],
)
def test_severity_rules(notes, severity):
    assert heuristic.extract(notes).severity is severity


def test_arrow_chain_becomes_steps():
    r = heuristic.extract("Upload fails\nopen settings -> click upload -> pick 20MB png")
    assert r.steps_to_reproduce == ["open settings", "click upload", "pick 20MB png"]


def test_turkish_notes():
    notes = "Hata: giriş sayfası çöküyor\n1. siteyi aç\n2. giriş yap\nbeklenen: ana sayfa\nolan: boş ekran\nSafari, iPhone 15"
    r = heuristic.extract(notes)
    assert r.title == "Giriş sayfası çöküyor"
    assert r.severity is Severity.high
    assert r.steps_to_reproduce == ["siteyi aç", "giriş yap"]
    assert r.expected == "ana sayfa"
    assert r.actual == "boş ekran"
    assert r.environment.device == "iPhone 15"
    assert "auth" in r.labels


def test_missing_info_lists_questions():
    r = heuristic.extract("The dashboard is broken")
    assert len(r.missing_info) == 4
    assert any("steps" in q for q in r.missing_info)


def test_long_title_is_truncated():
    r = heuristic.extract("x" * 200)
    assert len(r.title) == 80
    assert r.title.endswith("...")


def test_empty_notes_rejected():
    with pytest.raises(ValueError):
        heuristic.extract("   \n  ")


@pytest.mark.parametrize(
    ("notes", "expected_os"),
    [
        ("broken on windows 11", "Windows 11"),
        ("happens on macos 15", "macOS 15"),
        ("iphone on ios 18", "iOS 18"),
        ("android 15 tablet", "Android 15"),
        ("ubuntu desktop", "Ubuntu"),
    ],
)
def test_os_name_is_normalised(notes, expected_os):
    assert heuristic.extract("Title\n" + notes).environment.os == expected_os


def test_keywords_match_whole_words_not_substrings():
    report = heuristic.extract(
        "Rapid clicks discard the draft\n1. open the editor\n2. click save fast\nit took 1500ms"
    )
    assert "api" not in report.labels  # "rapid", "1500ms"
    assert "payment" not in report.labels  # "discard"
    assert report.component is None


def test_keyword_stems_still_match():
    report = heuristic.extract("Page freezes after login\nthe app is freezing")
    assert "performance" in report.labels  # "freez" stem
    assert "auth" in report.labels
