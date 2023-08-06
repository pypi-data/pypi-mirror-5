from detention.models import ActiveBan
import core
import signals
from django.contrib.auth import get_user_model
from django.utils.timezone import now as tznow
from django.utils.translation import ugettext_lazy as _
User = get_user_model()
__author__ = 'Luis'


class DetentionServiceError(Exception):

    def __init__(self, message, code):
        super(DetentionServiceError, self).__init__(message)
        self.code = code


class DetentionService(object):
    """
    Abstraction of a user ban service. This abstraction - a kind of
    manager - can ban, revert, and forgive a user.
    """

    def __init__(self, user):
        self.__user = user

    @staticmethod
    def _is_staff(user):
        return getattr(user, 'is_staff', False)

    @staticmethod
    def _is_superuser(user):
        return getattr(user, 'is_superuser', False)

    @staticmethod
    def _is_user_banneable(user):
        return not (DetentionService._is_staff(user) or DetentionService._is_superuser(user))

    def is_banneable(self):
        """
        Specifies wether this user is banneable or not.
        """

        return DetentionService._is_user_banneable(self.__user)

    def my_current_ban(self):
        """
        Gets the current ban for this user, if any ban applied.
        """

        if not self.is_banneable():
            return False
        else:
            current, terminated = core.check_ban_for(self.__user)
            if len(terminated):
                signals.bans_expired.send_robust(self.__user, current_ban=current, ban_list=terminated)
            return current

    def _check_can_ban(self, target):
        """
        Checks if this user can terminate this ban.
        """

        if not DetentionService._is_staff(self.__user):
            raise DetentionServiceError(_(u"Banner user must be staff"), "STAFF_REQUIRED")
        if self.__user == target:
            raise DetentionServiceError(_(u"Banner user and banned user must differ"), "CANNOT_BAN_SELF")
        if not isinstance(target, User):
            raise DetentionServiceError(_(u"Ban target must be a user instance"), "USER_REQUIRED")
        if not DetentionService._is_user_banneable(target):
            raise DetentionServiceError(_(u"Staff and super users can't be banned"), "NOT_BANNEABLE")

    def ban(self, target, duration, reason):
        """
        Creates a ban from this user to target user.
        """

        self._check_can_ban(target)
        core.clean_duration(duration)
        try:
            ban = core.add_ban(self.__user, target, duration, reason)
            signals.ban_applied.send_robust(target, new_ban=ban)
            return ban
        except Exception as e:
            raise DetentionServiceError(_(u"An internal error occurred when creating a ban "
                                    u"- Contact the administrator if this still happens"),
                                    "UNKNOWN")

    def _check_can_terminate(self, ban):
        """
        Checks if this user can terminate this ban.
        """

        if not DetentionService._is_staff(self.__user):
            raise DetentionServiceError(_(u"Reverter user must be staff"), "STAFF_REQUIRED")
        if not isinstance(ban, ActiveBan):
            raise DetentionServiceError(_(u"Only active bans can be reverted or forgiven"), "ACTIVEBAN_REQUIRED")
        if DetentionService._is_staff(ban.dictated_to) and not DetentionService._is_superuser(self.__user):
            raise DetentionServiceError(_(u"Even when bans in staff have no effect, only a super user can remove them"), "SUPERUSER_REQUIRED")
        if ban.dictated_by != self.__user and not DetentionService._is_superuser(self.__user):
            raise DetentionServiceError(_(u"Only a super user can revert or forgive a ban it did not create"), "SUPERUSER_REQUIRED")

    def revert(self, ban, reason):
        """
        Reverts an active ban.
        """

        self._check_can_terminate(ban)
        try:
            ban = core.revert_ban(self.__user, ban, tznow(), reason)
            signals.ban_terminated.send_robust(ban.dictated_to, ban=ban)
            return ban
        except Exception as e:
            raise DetentionServiceError(_(u"An internal error occurred when reverting a ban "
                                     u"- Contact the administrator if this still happens"),
                                     "UNKNOWN")

    def forgive(self, ban, reason):
        """
        Forgives an active ban.
        """

        self._check_can_terminate(ban)
        try:
            ban = core.forgive_ban(self.__user, ban, tznow(), reason)
            signals.ban_terminated.send_robust(ban.dictated_to, ban=ban)
            return ban
        except Exception as e:
            raise DetentionServiceError(_(u"An internal error occurred when forgiving a ban "
                                     u"- Contact the administrator if this still happens"),
                                     "UNKNOWN")

    @property
    def user(self):
        return self.__user