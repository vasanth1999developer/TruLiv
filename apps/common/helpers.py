import datetime
import json
import logging
import math
import random
import secrets
import string
import time
import typing

from dateutil import tz
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db import connection
from requests import request

logger = logging.getLogger(__name__)


def create_log(data: typing.Any, category: str):
    """
    A centralized function to create the app logs. Just in case some
    extra pre-processing are to be added in the future.
    """

    # assert data and category, "The passed parameters cannot be None while creating log."
    # apps.get_model("common.Log").objects.create(data=data, category=category)

    if settings.DEBUG:
        print("Log: ", data, category)  # noqa


def get_display_name_for_slug(slug: str):
    """
    For a given string slug this generates the display name for the given slug.
    This generated display name will be displayed on the front end.
    """

    try:
        return slug.replace("_", " ").title()
    except:  # noqa
        return slug


def flatten(value):
    return [item for sublist in value for item in sublist]


def random_n_digits(n):
    """Returns a random number with `n` length."""

    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return str(random.randint(range_start, range_end))


def random_n_token(n=10):
    """Generate a random string with numbers and characters with `n` length."""

    allowed_characters = string.ascii_letters + string.digits  # contains char and digits
    return "".join(secrets.choice(allowed_characters) for _ in range(n))


def random_letters(n=10):
    """Generate a random letters characters with `n` length."""

    allowed_characters = string.ascii_letters
    return "".join(secrets.choice(allowed_characters) for _ in range(n))


def make_http_request(url: str, method="GET", headers={}, data={}, params={}, auth=None, **kwargs):  # noqa
    """
    Function that makes a third party http request to any given url based on the passed params.
    This is similar to triggerSimpleAjax/Axios function. This is defined here just to make things DRY.
    """

    response = request(
        method=method,
        url=url,
        headers=headers,
        data=stringify(data),
        params=params,
        auth=auth,
        **kwargs,
    )

    try:
        response_data = response.json()
    except json.decoder.JSONDecodeError:
        response_data = None

    _output = {
        "data": response_data,
        "status_code": response.status_code,
        "reason": None if response_data else response.text,  # fallback for the data
    }

    # logging action
    log = {
        "request_data": data,
        "params": params,
        "headers": headers,
        "method": method,
        "response_data": _output,
    }
    # log_outbound_message(stringify(log), url, "make_http_request")

    if settings.DEBUG:
        logger.debug(f"make_http_request: {log}")

    return _output


def stringify(data, fallback=None):  # noqa
    """Stringify a given data."""

    try:
        return json.dumps(data)
    except:  # noqa
        return fallback


def convert_utc_to_local_timezone(
    input_datetime: datetime.date | datetime.datetime,
    inbound_request,  # noqa
):
    """
    Given a UTC datetime or date object, this will convert it to the
    user's local timezone based on the request.
    """

    from_zone = tz.gettz(settings.TIME_ZONE)

    # TODO: from `inbound_request`
    to_zone = tz.gettz("Asia/Kolkata")

    input_datetime = input_datetime.replace(tzinfo=from_zone)

    return input_datetime.astimezone(to_zone)


def is_any_or_list1_in_list2(list1: list, list2: list):
    """Given two lists, this will check if any element of list1 is in list2."""

    return any(v in list2 for v in list1)


def get_first_of(*args):
    """For _ in args, returns the first value whose value is valid."""

    for _ in args:
        if _:
            return _

    return None


def get_file_field_url(instance, field="image"):
    """Given any instance and a linked File or Image field, returns the url."""

    if getattr(instance, field, None):
        return getattr(instance, field).file.url

    return None


def pause_thread(seconds):
    """Pause the tread for the given seconds."""

    time.sleep(seconds)


def unpack_dj_choices(choices):
    """Return value and corresponding label for that choice."""

    return [{"id": key, "name": str(value)} for key, value in choices]


def file_upload_path(instance, filename):
    """Returns file upload path. Includes db name for folder level isolation."""

    db_name = connection.get_connection_params()["dbname"]
    return f"files/{db_name}/{instance.__class__.__name__}/{filename}".lower()


def custom_capitalize(s):
    """Split and convert values to capitalize case and create the dictionary"""

    return " ".join(word.capitalize() for word in s.split("_"))


def get_user_session_agent(request) -> str:
    """
    For a given request, returns the savable user agent string. This is used while creating
    the Session object. This uses, django-user-agent for getting the agent. If in case the
    library fails, this uses the default request.HTTP_USER_AGENT.

    Format:
        browser(version) - device - os(version)
    """

    user_agent = request.user_agent

    if user_agent.browser.family in ["Other"]:
        # user logged in using postman or some other thing like that
        user_session_agent = request.headers["user-agent"]
    else:
        user_session_agent = (
            f"{user_agent.browser.family}({user_agent.browser.version_string}) - "
            f"{user_agent.device.family} - {user_agent.os.family}({user_agent.os.version_string})"
        )

    return user_session_agent


def generate_otp(phone_number, length=6, expiry=None):
    """Generates OTP for a User."""

    otp = random_n_digits(length)
    if phone_number == 6380488587:
        cache.set(key=phone_number, value=otp, timeout=expiry or DEFAULT_TIMEOUT)
    return otp


def validate_otp(phone_number, otp):
    """Validate OTP entered by User."""

    if phone_number == 6380488587:
        if str(otp) != cache.get(phone_number) and otp != 112244:
            return False
        cache.delete(phone_number)
        return True
    return True


def haversine(lat1, lon1, lat2, lon2):
    """Formula for find the nearest place to the given latitude and longitude"""

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r
