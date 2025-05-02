from django.db import models
from django.utils.translation import gettext_lazy as _


class StateChoices(models.TextChoices):
    """
    Choices for all 50 US states using their standard 2-letter abbreviation.
    """

    ALABAMA = "AL", _("Alabama")
    ALASKA = "AK", _("Alaska")
    ARIZONA = "AZ", _("Arizona")
    ARKANSAS = "AR", _("Arkansas")
    CALIFORNIA = "CA", _("California")
    COLORADO = "CO", _("Colorado")
    CONNECTICUT = "CT", _("Connecticut")
    DELAWARE = "DE", _("Delaware")
    FLORIDA = "FL", _("Florida")
    GEORGIA = "GA", _("Georgia")
    HAWAII = "HI", _("Hawaii")
    IDAHO = "ID", _("Idaho")
    ILLINOIS = "IL", _("Illinois")
    INDIANA = "IN", _("Indiana")
    IOWA = "IA", _("Iowa")
    KANSAS = "KS", _("Kansas")
    KENTUCKY = "KY", _("Kentucky")
    LOUISIANA = "LA", _("Louisiana")
    MAINE = "ME", _("Maine")
    MARYLAND = "MD", _("Maryland")
    MASSACHUSETTS = "MA", _("Massachusetts")
    MICHIGAN = "MI", _("Michigan")
    MINNESOTA = "MN", _("Minnesota")
    MISSISSIPPI = "MS", _("Mississippi")
    MISSOURI = "MO", _("Missouri")
    MONTANA = "MT", _("Montana")
    NEBRASKA = "NE", _("Nebraska")
    NEVADA = "NV", _("Nevada")
    NEW_HAMPSHIRE = "NH", _("New Hampshire")
    NEW_JERSEY = "NJ", _("New Jersey")
    NEW_MEXICO = "NM", _("New Mexico")
    NEW_YORK = "NY", _("New York")
    NORTH_CAROLINA = "NC", _("North Carolina")
    NORTH_DAKOTA = "ND", _("North Dakota")
    OHIO = "OH", _("Ohio")
    OKLAHOMA = "OK", _("Oklahoma")
    OREGON = "OR", _("Oregon")
    PENNSYLVANIA = "PA", _("Pennsylvania")
    RHODE_ISLAND = "RI", _("Rhode Island")
    SOUTH_CAROLINA = "SC", _("South Carolina")
    SOUTH_DAKOTA = "SD", _("South Dakota")
    TENNESSEE = "TN", _("Tennessee")
    TEXAS = "TX", _("Texas")
    UTAH = "UT", _("Utah")
    VERMONT = "VT", _("Vermont")
    VIRGINIA = "VA", _("Virginia")
    WASHINGTON = "WA", _("Washington")
    WEST_VIRGINIA = "WV", _("West Virginia")
    WISCONSIN = "WI", _("Wisconsin")
    WYOMING = "WY", _("Wyoming")


class Services(models.IntegerChoices):
    SERVEILLANCE = 0, "Serveillance"
    DIAGNOSIS = 1, "Diagnosis"
    SCREENING = 2, "Screening"
    SECOND_OPINION = 3, "Second Opinion"
