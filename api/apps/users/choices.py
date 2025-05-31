# User roles
ADMIN = "Admin"
SALE = "Sales Representative"
REGULAR = "Regular User"

USER_ROLES = (
    (ADMIN, ADMIN),
    (SALE, SALE),
    (REGULAR, REGULAR),
)

# User status
PENDING = "Pending"
APPROVED = "Approved"
REJECTED = "Rejected"

USER_STATUS = (
    (PENDING, PENDING),
    (APPROVED, APPROVED),
    (REJECTED, REJECTED),
)

# Created via
ADMIN_SITE = "admin"
WEB = "web"
MOBILE = "mobile"

CREATED_VIA_CHOICES = (
    (ADMIN_SITE, ADMIN_SITE),
    (WEB, WEB),
    (MOBILE, MOBILE),
)

ACCEPT = "Accept"
DECLINE = "Decline"
EXPIRED = "Expired"

INVITE_STATUS = (
    (ACCEPT, ACCEPT),
    (DECLINE, DECLINE),
    (PENDING, PENDING),
    (EXPIRED, EXPIRED),
)

BLOCK_WALKER_MOBILE_APP = "blockwalker-mobile"
KINGMAKER_WEB = "kingmaker-web"
