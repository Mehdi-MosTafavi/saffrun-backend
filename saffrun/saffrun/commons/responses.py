class ErrorResponse:
    COLLISION_CODE = -1
    COLLISION_Messaage = "Collision with other reservations"
    INVALID_DATA = "invalid data"
    NOT_FOUND = "item not found"
    DATETIME_PRIORITY_ERROR = "start must be before end"
    DATETIME_A_DAY_ERROR = "your datetime should be in a single day"
    DURATION_ERROR = "duration couldn't be less than 5 minutes"


class SuccessResponse:
    CREATED = "created!"

    @staticmethod
    def reserve_created_message(count: int):
        return str(count) + " objects has been created!"
