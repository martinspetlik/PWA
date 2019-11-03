import os
import unittest
from mongoengine import *
from server.models.user import User
from server.models.message import Message
from server.models.conversation import Conversation


class TestUser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connect('mongoenginetest', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
       disconnect()

    def test_thing(self):
        User(name="test1", email="test@test1.com", password=os.urandom(16)).save()
        user = User.objects().first()
        self.assertEqual(user.name, 'test1')
        user = User.objects(name="test1").get()
        self.assertEqual(user.name, 'test1')


class TestConversation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connect('mongoenginetest', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
       disconnect()

    def test_thing(self):
        users = []
        users.append(User(name="test1", email="test@test1.com", password=os.urandom(16)).save())

        users.append(User(name="test2", email="test@test2.com", password=os.urandom(16)).save())

        saved_users = User.objects()
        self.assertEqual(len(saved_users), len(users))

        Conversation(members=users).save()

        conversation = Conversation.objects().first()

        self.assertEqual(len(conversation.members), len(users))
        for con_user, user in zip(conversation.members, users):
            self.assertEqual(con_user.name, user.name)
            self.assertEqual(con_user.email, user.email)


class TestMessage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connect('mongoenginetest', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
       disconnect()

    def test_thing(self):
        User(name="FooBar1", email="foo@bar1.com", password=os.urandom(16),).save()

        current_user = User.objects().first()
        users = User.objects()

        con = Conversation(members=users).save()

        Message(text="Message test text", author=current_user.id, conversation=con).save()

        message = Message.objects().first()
        self.assertEqual(message.author.id, current_user.id)
