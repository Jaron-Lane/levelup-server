import json
from rest_framework import status
from rest_framework.test import APITestCase
from levelupapi.models import GameType, Game

class GameTests(APITestCase):
    def setUp(self):
        """
        Create a new account and create sample category
        """
        url = "/register"
        data = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
            "bio": "Love those gamez!!"
        }
        # Initiate request and capture response
        response = self.client.post(url, data, format='json')

        # Parse the JSON in the response body
        json_response = json.loads(response.content)

        # Store the auth token
        self.token = json_response["token"]

        # Assert that a user was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # SEED DATABASE WITH ONE GAME TYPE
        # This is needed because the API does not expose a /gametypes
        # endpoint for creating game types
        gametype = GameType()
        gametype.label = "Board game"
        gametype.save()

    def test_create_game(self):
        """
        Ensure we can create a new game.
        """
        # DEFINE GAME PROPERTIES
        url = "/games"
        data = {
            "title": "Clue",
            "numberOfPlayers": 6,
            "description": "Its a mysterious game",
            "gameTypeId": 1,
            "gamer": 1
        }

        # Make sure request is authenticated
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Initiate request and store response
        response = self.client.post(url, data, format='json')

        # Parse the JSON in the response body
        json_response = json.loads(response.content)

        # Assert that the game was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the properties on the created resource are correct
        self.assertEqual(json_response["title"], "Clue")
        self.assertEqual(json_response["description"], "Its a mysterious game")
        self.assertEqual(json_response["number_of_players"], 6)
        self.assertEqual(json_response["gametype"]["id"], 1)
        self.assertEqual(json_response["gamer"]["id"], 1)

    def test_get_game(self):
        """
        Ensure we can get an existing game.
        """

        # Seed the database with a game
        game = Game()
        game.title = "Monopoly"
        game.gametype_id = 1
        game.number_of_players = 4
        game.gamer_id = 1
        game.description = "A really good time if you win"

        game.save()

        # Make sure request is authenticated
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Initiate request and store response
        response = self.client.get(f"/games/{game.id}")

        # Parse the JSON in the response body
        json_response = json.loads(response.content)

        # Assert that the game was retrieved
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the values are correct
        self.assertEqual(json_response["title"], "Monopoly")
        self.assertEqual(json_response["gametype"]["id"], 1)
        self.assertEqual(json_response["number_of_players"], 4)
        self.assertEqual(json_response["gamer"]["id"], 1)
        self.assertEqual(json_response["description"], "A really good time if you win")

    def test_change_game(self):
        """
        Ensure we can change an existing game.
        """
        game = Game()
        game.title = "Sorry"
        game.gametype_id = 1
        game.number_of_players = 4
        game.gamer_id = 1
        game.description = "Sucks to be you"
        game.save()

        # DEFINE NEW PROPERTIES FOR GAME
        data = {
            "title": "Sorry",
            "gameTypeId": 1,
            "numberOfPlayers": 4,
            "gamer": 1,
            "description": "Sorry suckaaa!"
        }

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(f"/games/{game.id}", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # GET GAME AGAIN TO VERIFY CHANGES
        response = self.client.get(f"/games/{game.id}")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # print(f"(Hello){type(json_response)}")

        # Assert that the properties are correct
        self.assertEqual(json_response["title"], "Sorry")
        self.assertEqual(json_response["gametype"]["id"], 1)
        self.assertEqual(json_response["number_of_players"], 4)
        self.assertEqual(json_response["gamer"]["id"], 1)
        self.assertEqual(json_response["description"], "Sorry suckaaa!")

    def test_delete_game(self):
        """
        Ensure we can delete an existing game.
        """
        game = Game()
        game.title = "Sorry"
        game.gametype_id = 1
        game.number_of_players = 4
        game.gamer_id = 1
        game.description = "Its a classic game we ALL know"
        game.save()

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(f"/games/{game.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # GET GAME AGAIN TO VERIFY 404 response
        response = self.client.get(f"/games/{game.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)