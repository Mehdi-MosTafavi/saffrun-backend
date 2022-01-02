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
    FULL_CAPACITY = "Full of capacity"
    USER_CLIENT = "The User should be client"
    USER_EMPLOYEE = "The User should be employee"
    INVALID_TYPE = 'type value could only be 1 or 2'
    SERVER_ERROR = "Najva server is not responsible"
    NOT_PROFILE_FOUND = "No profile found for user"
    USER_CLIENT = "The User should be client"
    USER_EMPLOYEE = "The User should be employee"
    INVALID_TYPE = 'type value could only be 1 or 2'
    SERVER_ERROR = "Najva server is not responsible"
    EMPLOYEE_NOT_FOUND = "Employee not found"



class SuccessResponse:
    CREATED = "created!"
    RESERVED = "reserved!"
    DELETED = "deleted!"
    CHANGED = "changed!"
    @staticmethod
    def reserve_created_message(count: int):
        return str(count) + " objects has been created!"
