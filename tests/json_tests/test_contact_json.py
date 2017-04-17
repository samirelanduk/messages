from unittest import TestCase
from unittest.mock import Mock
from pychats.json.contact_json import contact_to_json, json_to_contact
from pychats.chats.people import Contact

class ContactToJsonTests(TestCase):

    def test_can_make_json_from_contact(self):
        contact = Mock(Contact)
        contact.name.return_value = "Lord Asriel"
        json = contact_to_json(contact)
        self.assertEqual(json, {"name": "Lord Asriel"})


    def test_contact_to_json_requires_contact(self):
        with self.assertRaises(TypeError):
            contact_to_json("some string")



class JsonToContactTests(TestCase):

    def test_can_make_contact_from_json(self):
        json = {"name": "Lord Asriel"}
        contact = json_to_contact(json)
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact._name, "Lord Asriel")


    def test_contact_from_json_requires_dict(self):
        with self.assertRaises(TypeError):
            json_to_contact("some string")


    def test_contact_from_json_requires_name_key(self):
        with self.assertRaises(ValueError):
            json_to_contact({"wrongkey": "Lord Asriel"})