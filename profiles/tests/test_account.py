from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse

from profiles.models import Profile, Recommendation, User


class SignupViewTests(TestCase):

    def test_create(self):
        response = self.client.get(reverse('profiles:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(reverse('profiles:signup'), data={
            'name': 'Unit Test',
            'email': 'test@test.com',
            'password1': 'myunittest1!',
            'password2': 'myunittest1!',
            'g-recaptcha-response': 'abcdef',
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('username', response.context['form'].errors)

        response = self.client.post(reverse('profiles:signup'), data={
            'username': 'unittest',
            'name': 'Unit Test',
            'email': 'test@test.com',
            'password1': 'myunitarytest1!',
            'password2': 'myunitarytest1!',
            'g-recaptcha-response': 'abcdef',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND, 'form' in response.context and response.context['form'].errors.as_text())
        self.assertEqual(response.url, reverse('profiles:signup_confirm'))

        u = User.objects.get(email='test@test.com')
        token = response.context['token']
        uid = response.context['uid']

        response = self.client.get(reverse('profiles:signup_confirm'), data={
            'uid': uid,
            'token': token,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:login'))

    def test_account_page(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'test@test.com')

    def test_delete(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.save()

        p = Profile(contact_email='test@test.com', user=u)
        p.save()

        r = Recommendation(profile=p, reviewer_email='another@test.com')
        r.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user_delete'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        User.objects.get(id=u.id)

        response = self.client.post(reverse('profiles:user_delete'), data={
            'confirm': True,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:login'))

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=u.id)

        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(id=p.id)

        with self.assertRaises(Recommendation.DoesNotExist):
            Recommendation.objects.get(id=r.id)

    def test_account_changepassword(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.set_password('myunittest1!')
        u.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user_change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(reverse('profiles:user_change_password'), data={
            'old_password': 'myuqwdnittest1!!!',
            'new_password1': 'myunittest1!passchange',
            'new_password2': 'myunittest1!passchange',
        })

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('old_password', response.context['form'].errors)

        response = self.client.post(reverse('profiles:user_change_password'), data={
            'old_password': 'myunittest1!',
            'new_password1': 'myunittest1!passchange',
            'new_password2': 'myunittest1!passchange',
        })

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:user'))

    def test_profile_delete(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.save()

        p = Profile(contact_email='test@test.com', user=u)
        p.save()

        r = Recommendation(profile=p, reviewer_email='another@test.com')
        r.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user_profile_delete'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        User.objects.get(id=u.id)

        response = self.client.post(reverse('profiles:user_profile_delete'), data={
            'confirm': True,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:user'))

        p.refresh_from_db()
        self.assertNotEquals(p.deleted_at, None)

    def test_profile_delete(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.save()

        p = Profile(contact_email='test@test.com', user=u)
        p.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user_profile_delete'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        User.objects.get(id=u.id)

        response = self.client.post(reverse('profiles:user_profile_delete'), data={
            'confirm': True,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:user'))

        with self.assertRaises(Profile.DoesNotExist):
            p.refresh_from_db()
