from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock
from pychats.chats.conversations import Conversation, _sort_messages
from pychats.chats.people import Contact
from pychats.chats.messages import Message

class ConversationTest(TestCase):

    def setUp(self):
        self.senders = [Mock(Contact) for _ in range(5)]
        self.messages = [Mock(Message) for _ in range(5)]
        for index, message in enumerate(self.messages):
            message.timestamp.return_value = datetime(2009, 5, index + 1, 12)
            message.sender.return_value = self.senders[index % 3]
            message._conversation = None



class ConversationCreationTests(ConversationTest):

    def test_can_create_conversation(self):
        conversation = Conversation()
        self.assertEqual(conversation._messages, [])
        self.assertEqual(conversation._chatlog, None)



class ConversationFromJsonTests(TestCase):

    @patch("pychats.chats.conversations._sort_messages")
    @patch("pychats.chats.conversations.Message.from_json")
    def test_can_create_conversation_from_json(self, mock_message, mock_sort):
        message1, message2, message3 = Mock(), Mock(), Mock()
        mock_message.side_effect = [message1, message2, message3]
        json = {
         "messages": ["message1", "message2", "message3"]
        }
        mock_sort.side_effect = lambda k: k
        conversation = Conversation.from_json(json)
        mock_message.assert_any_call("message1")
        mock_message.assert_any_call("message2")
        mock_message.assert_any_call("message3")
        self.assertIsInstance(conversation, Conversation)
        self.assertEqual(conversation._messages, [message1, message2, message3])
        mock_sort.assert_called_with([message1, message2, message3])


    def test_json_to_conversation_requires_dict(self):
        with self.assertRaises(TypeError):
            Conversation.from_json("some string")


    def test_json_to_message_requires_messages_key(self):
        with self.assertRaises(ValueError):
            Conversation.from_json({"wrong": []})



class ConversationMergingTests(TestCase):

    @patch("pychats.chats.conversations._sort_messages")
    def test_can_merge_conversations(self, mock_sort):
        conv1 = Mock(Conversation)
        conv2 = Mock(Conversation)
        conv3 = Mock(Conversation)
        message1, message2, message3 = [Mock(), Mock(), Mock()]
        message4, message5, message6 = [Mock(), Mock(), Mock()]
        message7, message8, message9 = [Mock(), Mock(), Mock()]
        conv1.messages.return_value = [message1, message2, message3]
        conv2.messages.return_value = [message4, message5, message6]
        conv3.messages.return_value = [message7, message8, message9]
        message3.__eq__ = MagicMock()
        message4.__eq__ = MagicMock()
        message6.__eq__ = MagicMock()
        message7.__eq__ = MagicMock()
        message3.__eq__.side_effect = lambda o: o is message4
        message4.__eq__.side_effect = lambda o: o is message3
        message6.__eq__.side_effect = lambda o: o is message7
        message7.__eq__.side_effect = lambda o: o is message6
        mock_sort.return_value = "sorted messages"
        conv4 = Conversation.merge(conv1, conv2, conv3)
        mock_sort.assert_called_with([
         message1, message2, message3, message5, message6, message8, message9
        ])
        self.assertEqual(conv4._messages, "sorted messages")


    def test_conversation_merging_requires_conversations(self):
        conv1 = Mock(Conversation)
        conv2 = Mock(Message)
        conv3 = Mock(Conversation)
        conv1.messages.return_value, conv3.messages.return_value = [], []
        with self.assertRaises(TypeError):
            Conversation.merge(conv1, conv2, conv3)



class ConversationReprTests(ConversationTest):

    def test_conversation_repr_no_messages(self):
        conversation = Conversation()
        self.assertEqual(str(conversation), "<Conversation (0 messages)>")


    def test_conversation_repr_one_message(self):
        conversation = Conversation()
        conversation._messages.append(Mock(Message))
        self.assertEqual(str(conversation), "<Conversation (1 message)>")


    def test_conversation_repr_multiple_message(self):
        conversation = Conversation()
        conversation._messages.append(Mock(Message))
        conversation._messages.append(Mock(Message))
        self.assertEqual(str(conversation), "<Conversation (2 messages)>")
        conversation._messages.append(Mock(Message))
        self.assertEqual(str(conversation), "<Conversation (3 messages)>")



class ConversationLenTests(ConversationTest):

    @patch("pychats.chats.conversations.Conversation.length")
    def test_len_returns_length(self, mock_length):
        mock_length.return_value = 23
        conversation = Conversation()
        self.assertEqual(len(conversation), 23)



class ConversationMessagesTests(ConversationTest):

    def test_messages_returns_messages(self):
        conversation = Conversation()
        for message in self.messages:
            conversation._messages.append(message)
        self.assertEqual(conversation._messages, conversation.messages())
        self.assertIsNot(conversation._messages, conversation.messages())



class ConversationMessageAdditionTests(ConversationTest):

    def test_can_add_messages_to_conversation(self):
        conversation = Conversation()
        conversation.add_message(self.messages[0])
        self.assertEqual(conversation._messages, [self.messages[0]])
        conversation.add_message(self.messages[1])
        self.assertEqual(conversation._messages, self.messages[0:2])


    def test_can_only_add_messages_to_conversations(self):
        conversation = Conversation()
        with self.assertRaises(TypeError):
            conversation.add_message("Some message")


    def test_cannot_add_message_if_it_is_already_present(self):
        conversation = Conversation()
        conversation.add_message(self.messages[0])
        with self.assertRaises(ValueError):
            conversation.add_message(self.messages[0])


    def test_adding_messages_updates_conversation_of_messages(self):
        conversation = Conversation()
        self.assertIs(self.messages[0]._conversation, None)
        conversation.add_message(self.messages[0])
        self.assertIs(self.messages[0]._conversation, conversation)


    def test_adding_messages_will_order_them_by_date(self):
        conversation = Conversation()
        conversation.add_message(self.messages[2])
        self.assertEqual(conversation._messages, [self.messages[2]])
        conversation.add_message(self.messages[1])
        self.assertEqual(conversation._messages, self.messages[1:3])
        conversation.add_message(self.messages[0])
        self.assertEqual(conversation._messages, self.messages[:3])
        conversation.add_message(self.messages[4])
        self.assertEqual(conversation._messages, self.messages[:3] + [self.messages[-1]])
        conversation.add_message(self.messages[3])
        self.assertEqual(conversation._messages, self.messages)



class ConversationMessageRemovalTests(ConversationTest):

    def test_can_remove_messages(self):
        conversation = Conversation()
        conversation._messages = list(self.messages)
        conversation.remove_message(self.messages[-1])
        self.assertEqual(conversation._messages, self.messages[:-1])
        conversation.remove_message(self.messages[0])
        self.assertEqual(conversation._messages, self.messages[1:-1])
        conversation.remove_message(self.messages[2])
        self.assertEqual(
         conversation._messages,
         [self.messages[1], self.messages[3]]
        )


    def test_removing_messages_resets_message_conversation_to_none(self):
        conversation = Conversation()
        conversation._messages = [self.messages[0]]
        conversation._messages[0]._conversation = conversation
        self.assertIs(self.messages[0]._conversation, conversation)
        conversation.remove_message(self.messages[0])
        self.assertIs(self.messages[0]._conversation, None)



class ConversationLengthTests(ConversationTest):

    def test_length_returns_number_of_messages(self):
        conversation = Conversation()
        conversation._messages = self.messages
        self.assertEqual(conversation.length(), 5)



class ConversationChatlogTests(ConversationTest):

    def test_can_access_chatlog(self):
        conversation = Conversation()
        chatlog = "..."
        conversation._chatlog = chatlog
        self.assertIs(conversation.chatlog(), chatlog)



class ConversationParticipantTests(ConversationTest):

    def test_can_get_conversation_participants(self):
        conversation = Conversation()
        self.assertEqual(conversation.participants(), set())
        conversation.add_message(self.messages[0])
        self.assertEqual(
         conversation.participants(),
         set([self.senders[0]])
        )
        conversation.add_message(self.messages[1])
        self.assertEqual(
         conversation.participants(),
         set(self.senders[0:2])
        )
        conversation.add_message(self.messages[2])
        self.assertEqual(
         conversation.participants(),
         set(self.senders[0:3])
        )
        conversation.add_message(self.messages[3])
        self.assertEqual(
         conversation.participants(),
         set(self.senders[0:3])
        )
        conversation.add_message(self.messages[4])
        self.assertEqual(
         conversation.participants(),
         set(self.senders[0:3])
        )



class SortMessagesTests(ConversationTest):

    def test_can_sort_messages(self):
        messages = self.messages[2:5][::-1] + self.messages[:2]
        self.assertEqual(_sort_messages(messages), self.messages)



class ConversationToJsonTests(ConversationTest):

    def test_can_get_json_from_conversation(self):
        self.messages[0].to_json.return_value = {"aa": "bb"}
        self.messages[1].to_json.return_value = {"cc": "dd"}
        conversation = Conversation()
        conversation._messages = self.messages[:2]
        self.assertEqual(
         conversation.to_json(), {"messages": [{"aa": "bb"}, {"cc": "dd"}]}
        )
        self.messages[0].to_json.assert_called_with()
        self.messages[1].to_json.assert_called_with()


    def test_can_get_json_from_conversation_with_attachemts(self):
        self.messages[0].to_json.return_value = {"aa": "bb"}
        self.messages[1].to_json.return_value = {"cc": "dd"}
        conversation = Conversation()
        conversation._messages = self.messages[:2]
        self.assertEqual(
         conversation.to_json(attachment_path="path"),
         {"messages": [{"aa": "bb"}, {"cc": "dd"}]}
        )
        self.messages[0].to_json.assert_called_with(attachment_path="path")
        self.messages[1].to_json.assert_called_with(attachment_path="path")
