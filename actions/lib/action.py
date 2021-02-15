from st2common.runners.base_action import Action

import requests


__all__ = ["NetboxBaseAction"]


class NetboxBaseAction(Action):
    """Base Action for all Netbox API based actions"""

    def __init__(self, config):
        super(NetboxBaseAction, self).__init__(config)

    def make_request(self, endpoint_uri, http_action, **kwargs):
        """Logic to make all types of requests"""

        if self.config["use_https"]:
            url = "https://"
        else:
            url = "http://"

        url = url + self.config["hostname"] + "/api" + endpoint_uri

        headers = {
            "Authorization": "Token " + self.config["api_token"],
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # transform `in__id` if present
        if kwargs.get("id__in"):
            kwargs["id__in"] = ",".join(kwargs["id__in"])
            self.logger.debug("id__in transformed to {}".format(kwargs["id__in"]))

        # transform `tags` if present
        if kwargs.get("tags"):
            kwargs["tags"] = ",".join(kwargs["tags"])
            self.logger.debug("tags transformed to {}".format(kwargs["tags"]))

        # strip values which have a None value if we are making a write request
        if http_action != "get":
            kwargs = {key: value for key, value in kwargs.items() if value is not None}

        self.logger.debug("Calling base {} with kwargs: {}".format(http_action, kwargs))
        verify = self.config["ssl_verify"]

        if http_action == "get":
            r = requests.get(url, verify=verify, headers=headers, params=kwargs)

        elif http_action == "post":
            r = requests.post(url, verify=verify, headers=headers, json=kwargs)

        elif http_action == "put":
            r = requests.put(url, verify=verify, headers=headers, json=kwargs)

        elif http_action == "patch":
            r = requests.patch(url, verify=verify, headers=headers, json=kwargs)

        elif http_action == "delete":
            r = requests.delete(url, verify=verify, headers=headers)
            self.logger.info(
                "Delete of ID {} returned status code {}".format(kwargs["id"], r.status_code)
            )

        return r
