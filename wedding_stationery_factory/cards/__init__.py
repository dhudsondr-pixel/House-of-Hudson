"""Wedding card type registry."""

from .details import build as build_details
from .invitation import build as build_invitation
from .menu import build as build_menu
from .rsvp import build as build_rsvp
from .save_the_date import build as build_save_the_date
from .thank_you import build as build_thank_you


CARD_TYPES = {
    "save-the-date": {
        "build": build_save_the_date,
        "display_name": "Save the Date",
        "size": "7x5",
        "keywords": ("save the date", "save our date", "wedding announcement",
                     "save the date card", "engagement announcement"),
        "etsy_category": "Weddings > Paper & Party Supplies",
        "page_count": 1,
    },
    "invitation": {
        "build": build_invitation,
        "display_name": "Wedding Invitation",
        "size": "5x7",
        "keywords": ("wedding invitation", "invitation template",
                     "printable invitation", "wedding suite",
                     "fillable invitation"),
        "etsy_category": "Weddings > Paper & Party Supplies",
        "page_count": 1,
    },
    "rsvp-card": {
        "build": build_rsvp,
        "display_name": "RSVP Card",
        "size": "5x3.5",
        "keywords": ("rsvp card", "wedding rsvp", "response card",
                     "reply card", "rsvp printable"),
        "etsy_category": "Weddings > Paper & Party Supplies",
        "page_count": 1,
    },
    "details-card": {
        "build": build_details,
        "display_name": "Details Card",
        "size": "5x3.5",
        "keywords": ("details card", "wedding details", "info card",
                     "directions card", "accommodation card"),
        "etsy_category": "Weddings > Paper & Party Supplies",
        "page_count": 1,
    },
    "menu": {
        "build": build_menu,
        "display_name": "Wedding Menu",
        "size": "4x9",
        "keywords": ("wedding menu", "menu template", "reception menu",
                     "dinner menu", "menu card"),
        "etsy_category": "Weddings > Paper & Party Supplies",
        "page_count": 1,
    },
    "thank-you-card": {
        "build": build_thank_you,
        "display_name": "Thank You Card",
        "size": "5x3.5",
        "keywords": ("wedding thank you", "thank you card", "thank you template",
                     "thank you note", "wedding thanks"),
        "etsy_category": "Weddings > Paper & Party Supplies",
        "page_count": 1,
    },
}
