from rest_framework import status


class VsionResponse:
    def __init__(self, api_type):
        self.api_type = api_type

    def create_response_object(self, status, message, data={}, detail=None):
        res = {
            "status": status,
            "message": message,
        }

        if data or isinstance(data, list):
            res = {**res, "data": data}

        if detail:
            res = {**res, "detail": detail}

        return res

    def internal_server_error(self, e='An unknown error found!'):
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return (
            self.create_response_object(
                response_status,
                "Internal Server Error",
                detail=e
            ),
            response_status,
        )

    def params_invalid(self, params):
        response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        return (
            self.create_response_object(
                response_status,
                f"Invalid params, {params} is not an ObjectId",
            ),
            response_status,
        )

    def data_not_found(self, id):
        response_status = status.HTTP_404_NOT_FOUND
        return (
            self.create_response_object(
                response_status,
                f"Failed to fetch {self.api_type}",
                None,
                f"{self.api_type} {id} doesn't exist!",
            ),
            response_status,
        )

    """ This section is for GET Method"""

    def list_success(self, data):
        data = dict(data)
        response_status =  status.HTTP_200_OK
            
        response_obj = self.create_response_object(
            response_status,
            f"Success get list {self.api_type}",
            data["results"],
        )

        del data["results"]

        response_obj = {**response_obj, **data}
        return response_obj, response_status

    def list_failed(self, detail):
        response_status = status.HTTP_400_BAD_REQUEST

        response_obj = self.create_response_object(
            response_status,
            f"Failed get {self.api_type}",
            None,
            detail,
        )

        return response_obj, response_status

    def retrieve_success(self, params, data):
        response_status = status.HTTP_200_OK

        return (
            self.create_response_object(
                response_status,
                f"Success get {self.api_type} {params}",
                data,
            ),
            response_status,
        )

    def retrieve_failed(self, params, detail):
        response_status = status.HTTP_400_BAD_REQUEST

        response_obj = self.create_response_object(
            response_status,
            f"Failed get {self.api_type} {params}",
            None,
            detail,
        )

        return response_obj, response_status

    """ End section for get method"""

    """ This section is for post method"""

    def create_success(self, data):
        response_status = (
            status.HTTP_200_OK if (len(data) > 0) else status.HTTP_404_NOT_FOUND
        )

        return (
            self.create_response_object(
                response_status,
                f"Success create {self.api_type}",
                data,
            ),
            response_status,
        )

    def create_failed(self, detail=None):
        response_status = (
            status.HTTP_422_UNPROCESSABLE_ENTITY
            if (type(detail) == "string")
            else status.HTTP_400_BAD_REQUEST
        )

        response_obj = self.create_response_object(
            response_status,
            f"Failed create {self.api_type}",
            None,
            detail,
        )

        return response_obj, response_status

    """ End section for post method"""

    """ This section is for delete method """

    def delete_success(self, id):
        response_status = status.HTTP_200_OK
        return (
            self.create_response_object(
                response_status,
                f"Success delete {self.api_type} {id}",
            ),
            response_status,
        )

    def delete_not_found(self, id):
        response_status = status.HTTP_204_NO_CONTENT
        return (
            self.create_response_object(
                response_status,
                f"{self.api_type} {id} doesn't exist, no need to delete it!",
            ),
            response_status,
        )

    def delete_failed(self, id):
        response_status = status.HTTP_400_BAD_REQUEST
        return (
            self.create_response_object(
                response_status,
                f"Failed to delete {self.api_type} {id}!",
            ),
            response_status,
        )

    """ End section for delete method"""
