import json

from lib.action import NetboxBaseAction
from st2client.client import Client
from st2client.models import KeyValuePair


class NetboxHTTPAction(NetboxBaseAction):
    """
    Base run action
    """

    def run(self, endpoint_uri, http_verb, get_detail_route_eligible, **kwargs):
        """
        Base run action
        """
        return_result = None
        return_status = None

        if http_verb == "get":
            if kwargs.get("id", False) and get_detail_route_eligible:
                # modify the `endpoint_uri` to use the detail route
                endpoint_uri = "{}{}/".format(endpoint_uri, str(kwargs.pop("id")))
                self.logger.debug(
                    "endpoint_uri transformed to {} because id was passed".format(endpoint_uri)
                )

        result = self.make_request(endpoint_uri, http_verb, **kwargs)
        return_status = result.ok

        if return_status is True and http_verb == "get":
            if kwargs.get("save_in_key_store", False) is True:
                key_name = kwargs.get("save_in_key_store_key_name")
                if not key_name:
                    return_status, return_result = (
                        False,
                        "save_in_key_store_key_name MUST be used with save_in_key_store!",
                    )
                else:
                    # save the result in the st2 keystore
                    # FIXME: This shouldn't be hard coded and will break on systems where the api
                    #        is not listening on localhost.
                    client = Client(base_url="http://localhost")
                    # FIXME: This call could raise exceptions and should probably be caught and
                    #        handled correctly for better error reporting to users.
                    client.keys.update(
                        KeyValuePair(
                            name=key_name,
                            value=json.dumps(result.json()),
                            ttl=kwargs["save_in_key_store_ttl"],
                        )
                    )

                    return_status = True
                    return_result = "Result stored in st2 key {}".format(key_name)
        else:
            return_result = result.json()

        return (return_status, {"raw": return_result})
