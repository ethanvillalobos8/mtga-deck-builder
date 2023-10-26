class Card:
    def __init__(self, name, card_type, mana_cost, text, abilities=None):
        if abilities is None:
            abilities = []
        self.name = name
        self.card_type = card_type
        self.mana_cost = mana_cost
        self.text = text
        self.abilities = abilities
        self.status = "untapped"
        self.summoning_sick = True if card_type == "creature" else False

    def tap(self):
        self.status = "tapped"

    def untap(self):
        self.status = "untapped"

    def __str__(self):
        return f"Name: {self.name}, Type: {self.card_type}, ManaCost: {self.mana_cost}, Text: {self.text}"


class LandCard(Card):
    def __init__(self, name, mana_output, text="", abilities=None):
        super().__init__(name, "land", 0, None, None)
        self.mana_output = mana_output

    def tap_for_mana(self, player):
        if self.status == "untapped":
            self.tap()
            for color, amount in self.mana_output.items():
                player.mana_pool[color] += amount


class CreatureCard(Card):
    def __init__(self, name, mana_cost, power, toughness, text, damage=0, abilities=None):
        super().__init__(name, "creature", mana_cost, text, abilities)
        self.power = power
        self.toughness = toughness
        self.damage = damage
        self.summoning_sick = True
