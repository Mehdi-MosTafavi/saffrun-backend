class ErrorResponse:
    COLLISION_CODE = -1
    COLLISION_Messaage = "Collision with other reservations"
    INVALID_DATA = "invalid data"
    NOT_FOUND = "item not found"
    DATETIME_PRIORITY_ERROR = "start must be before end"
    DATETIME_A_DAY_ERROR = "your datetime should be in a single day"
    DURATION_ERROR = "duration couldn't be less than 5 minutes"
    DURATION_OR_COUNT_ERROR = (
        "You should pass one of duration or count parameter to server"
    )
    DID_NOT_FOLLOW = "Did not following"
    FOLLOWING_BEFORE = "Following before"
    NOT_ENOUGH_DATA = "Not enough data"
    NO_CLIENT_HEADER = "No Client field in header"
    FULL_CAPACITY = "Full of capacity"


class SuccessResponse:
    CREATED = "created!"
    RESERVED = "reserved!"

    @staticmethod
    def reserve_created_message(count: int):
        return str(count) + " objects has been created!"
