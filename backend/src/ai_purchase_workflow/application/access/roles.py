from enum import StrEnum


class ApplicationRole(StrEnum):
    REQUESTER = "requester"
    APPROVER = "approver"
    ADMIN = "admin"
