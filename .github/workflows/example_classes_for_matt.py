
from copy import deepcopy


class AMPlayer:

    def __init__(self, name="NOT SET"):

        self.name = name
        self.hair_colour = "black"
        self.favorite_dish = "pain"

        self._characters = []  # Dara's ars magica character

    def is_hair_colour_black(self):
        return self.hair_colour == "black"

    def is_hair_colour_sane(self, sane_hair_colours=("black", "grey", "green")):
        return self.hair_colour in sane_hair_colours

    def add_character(self, character_name):
        assert isinstance(character_name, str), "character name has to be a string"
        self._characters.append(character_name)

    def __str__(self):
        return "name: " + self.name + "\n" + "characters: " + str(self._characters)




dara = AMPlayer(name="Dara")
dara.add_character("this is a test name")
dara.hair_colour = "green"
print(dara.hair_colour)

print(str(dara))






