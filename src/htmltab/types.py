import requests
import requests.exceptions
from click.types import ParamType
from click.utils import safecall


class URL(ParamType):
    """
    Declare a parameter to be a URL as understood by ``urllib``. The URL
    is requested using the GET method and the connection is closed once
    the context is closed (the command finishes execution).
    """

    name = "url"
    USER_AGENT = "HTMLTab (+https://github.com/flother/htmltab)"

    def convert(self, value, param, ctx):
        """
        Opens the parameter value as a URL using
        ``urllib.request.urlopen``. A custom User-Agent header is used
        and a ten-second timeout is set, but otherwise no alterations
        are made to the defaults (i.e. no authentication, no cookies).
        Any error causes the command to fail.
        """
        try:
            response = requests.get(
                value, timeout=10, headers={"User-Agent": self.USER_AGENT}
            )
            if ctx is not None:
                ctx.call_on_close(safecall(response.close))
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            self.fail(f"Connection error ({value})", param, ctx)
        except requests.exceptions.Timeout:
            self.fail(f"Time out ({value})", param, ctx)
        except requests.exceptions.TooManyRedirects:
            self.fail(f"Too many redirects ({value})", param, ctx)
        except requests.exceptions.HTTPError:
            self.fail(
                f"HTTP {response.status_code} {response.reason} ({value})",
                param,
                ctx,
            )
        except requests.exceptions.RequestException:
            self.fail(f"Request error ({value})", param, ctx)
        return response
