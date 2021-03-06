# coding: utf-8

import unittest

from django.contrib.auth.models import User
from django.core import mail
from django.utils import timezone
from django.conf import settings

from test.factories import UserFactory
from users.models import UserAuthCode, create_new_user, activate_user


class UserAuthCodeTest(unittest.TestCase):

    def setUp(self):
        self.encoder = UserAuthCode('secret')
        self.user = UserFactory(is_active=False)

    def tearDown(self):
        self.encoder = None
        self.user.delete()
        self.user = None

    def test_user(self):
        self.assertIsNotNone(self.user.date_joined)
        self.assertTrue(self.user.date_joined >= self.user.last_login)

    def test_salt(self):
        salt = self.encoder.salt()
        self.assertEqual(8, len(salt))

    def test_auth_code(self):
        code = self.encoder.auth_code(self.user)
        self.assertIsNotNone(code)

    def test_complete_activation(self):
        code = self.encoder.auth_code(self.user)
        self.assertTrue(self.encoder.is_valid(self.user, code))

    def test_wrong_key(self):
        self.assertFalse(self.encoder.is_valid(self.user, 'aaa'))

    def test_already_activated(self):
        code = self.encoder.auth_code(self.user)
        self.user.last_login = timezone.now()
        self.user.save()
        self.assertFalse(self.encoder.is_valid(self.user, code))


class UserTest(unittest.TestCase):
    '''User-specific tests'''
    def setUp(self):
        self.user = UserFactory.build(
            first_name='Boy',
            last_name='Factory'
        )

    def tearDown(self):
        self.user = None

    def test_user(self):
        self.assertNotEqual(None, self.user)

    def test_user_first_name(self):
        self.assertEqual('Boy', self.user.first_name)

    def test_user_last_name(self):
        self.assertEqual('Factory', self.user.last_name)

    def test_user_email(self):
        self.assertEqual('boy_factory@example.com', self.user.email)


class TestUserCreation(unittest.TestCase):
    def setUp(self):
        user = UserFactory.build()
        self.user = create_new_user(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password='123'
        )

    def tearDown(self):
        # clear outbox
        mail.outbox.pop()
        self.user.delete()

    def test_create_new_user(self):
        self.assertEqual(1, User.objects.all().count())

    def test_user_password(self):
        u = User.objects.get(email=self.user.email)
        self.assertTrue(u.check_password('123'))

    def test_user_staff(self):
        u = User.objects.get(email=self.user.email)
        self.assertFalse(u.is_staff)

    def test_user_active(self):
        u = User.objects.get(email=self.user.email)
        self.assertFalse(u.is_active)

    def test_send_email(self):
        self.assertEqual(1, len(mail.outbox))

    def test_email_subject(self):
        self.assertEqual(
            mail.outbox[0].subject,
            u'Активация учетной записи'
        )


class TestUserActivation(unittest.TestCase):
    def setUp(self):
        encoder = UserAuthCode(settings.SECRET_KEY)
        self.user = UserFactory(is_active=False)
        self.code = encoder.auth_code(self.user)

    def tearDown(self):
        self.user.delete()
        self.code = None

    def test_user_activation(self):
        self.assertTrue(activate_user(self.user, self.code))
        self.assertTrue(self.user.is_active)

    def test_wrong_code(self):
        self.assertFalse(activate_user(self.user, 'self.code'))
        self.assertFalse(self.user.is_active)
