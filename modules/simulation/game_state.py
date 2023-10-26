import random
from modules.simulation.cards import Card, LandCard, CreatureCard
from time import sleep


def parse_mana_cost(mana_string):
    colors = ['W', 'U', 'B', 'R', 'G']
    mana_dict = {}
    for color in colors:
        mana_dict[color] = mana_string.count('{' + color + '}')
        mana_string = mana_string.replace('{' + color + '}', '')

    # Remove hybrid mana indicators
    for char in ['/', 'P']:
        mana_string = mana_string.replace(char, '')

    generic_mana = ''.join([ch for ch in mana_string if ch.isdigit()])
    mana_dict['C'] = int(generic_mana) if generic_mana else 0
    return mana_dict


def get_card_details_by_name(card_name, card_catalog):
    card_details = card_catalog[card_catalog['Name'] == card_name].iloc[0].to_dict()
    card_details['ManaCost'] = parse_mana_cost(card_details.pop('Mana Cost'))  # Parse 'Mana Cost' to dictionary

    if 'Power' in card_details and card_details['Power'] != 'Unknown':
        card_details['Power'] = int(card_details['Power'])
    if 'Toughness' in card_details and card_details['Toughness'] != 'Unknown':
        card_details['Toughness'] = int(card_details['Toughness'])

    return card_details


def shuffle_deck(deck_dict, card_catalog):
    deck_list = []
    for card_name, quantity in deck_dict.items():
        card_details = get_card_details_by_name(card_name, card_catalog)
        card_type = card_details['Type']
        mana_cost = card_details.get('ManaCost', None)
        card_text = card_details['Text']

        if "creature" in card_type.lower():
            power = card_details['Power']
            toughness = card_details['Toughness']
            card = CreatureCard(card_name, mana_cost, power, toughness, card_text)
        else:
            card = Card(card_name, card_type, mana_cost, card_text)

        deck_list.extend([card] * quantity)

    random.shuffle(deck_list)
    return deck_list


def print_deck_details(deck_list):
    for card in deck_list:
        print(card)


class Player:
    def __init__(self, deck_dict, card_catalog, name="Player", life=20):
        self.name = name
        self.deck = shuffle_deck(deck_dict, card_catalog)
        self.life = life
        self.played_land_this_turn = False
        self.hand = []
        self.board = []
        self.graveyard = []
        self.exile = []
        self.mana_pool = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        self.attackers = []
        self.blockers = []

    def draw_card(self):
        if self.deck:
            drawn_card = self.deck.pop(0)
            self.hand.append(drawn_card)

    def add_mana_to_mana_pool(self, land_type):
        lands = {"Plains": "W", "Island": "U", "Swamp": "B", "Mountain": "R", "Forest": "G"}
        for land in lands.keys():
            if land_type == land:
                mana_symbol = lands[land]  # Access the value associated with the key 'land'
                self.mana_pool[mana_symbol] += 1

    def use_mana(self, mana_cost):
        total_mana_available = sum(self.mana_pool.values())

        # Check and deduct colored mana costs
        for color, amount in mana_cost.items():
            if color != 'C':
                if self.mana_pool[color] < amount:
                    return False
                self.mana_pool[color] -= amount
                total_mana_available -= amount

        # Check if there's enough mana left (of any type) for the colorless portion
        if total_mana_available < mana_cost.get('C', 0):
            return False

        # Deduct the colorless portion from the mana pool (preferring to use actual colorless mana first)
        colorless_needed = mana_cost.get('C', 0)
        if self.mana_pool['C'] >= colorless_needed:
            self.mana_pool['C'] -= colorless_needed
        else:
            colorless_needed -= self.mana_pool['C']
            self.mana_pool['C'] = 0
            for color in self.mana_pool:
                if colorless_needed == 0:
                    break
                if self.mana_pool[color] > 0:
                    deduction = min(self.mana_pool[color], colorless_needed)
                    self.mana_pool[color] -= deduction
                    colorless_needed -= deduction

        return True

    def play_card(self, card):
        if card in self.hand:
            if "land" in card.card_type.lower():
                if not self.played_land_this_turn:
                    self.board.append(card)
                    self.hand.remove(card)
                    self.add_mana_to_mana_pool(card.name)
                    if isinstance(card, LandCard):
                        card.tap_for_mana(self)
                    self.played_land_this_turn = True
                    print(f"{self.name} played {card.name}. Remaining hand: {[c.name for c in self.hand]}")  # Debug
            elif "creature" in card.card_type.lower():
                if self.use_mana(card.mana_cost):
                    self.board.append(card)
                    card.summoning_sick = True
                    self.hand.remove(card)
                    print(f"{self.name} played {card.name}. Remaining hand: {[c.name for c in self.hand]}")  # Debug


class BoardState:
    def __init__(self, player1, player2):
        self.active_player = player1
        self.non_active_player = player2
        self.stack = []
        self.phases = ["Beginning Phase", "Pre-combat Main Phase", "Combat Phase", "Post-combat Main Phase",
                       "Ending Phase"]
        self.current_phase = self.phases[0]

    def simulate_turn(self):
        print("\n--- Beginning Phase ---")
        self.beginning_phase()

        print("\n--- Pre-combat Main Phase ---")
        self.pre_combat_main_phase()

        print("\n--- Combat Phase ---")
        self.combat_phase()

        print("\n--- Post-combat Main Phase ---")
        self.post_combat_main_phase()

        print("\n--- Ending Phase ---")
        self.ending_phase()

        self.active_player.attackers.clear()
        self.active_player.blockers.clear()
        self.non_active_player.attackers.clear()
        self.non_active_player.blockers.clear()

        # Swap active and non-active players for the next turn
        self.active_player, self.non_active_player = self.non_active_player, self.active_player

    def upkeep(self):
        pass

    def beginning_phase(self):
        # Reset land played flag
        self.active_player.played_land_this_turn = False

        # Check if the player needs to discard due to no initial lands
        if hasattr(self.active_player, 'needs_to_discard') and self.active_player.needs_to_discard:
            discarded_card = random.choice(self.active_player.hand)
            self.active_player.hand.remove(discarded_card)
            self.active_player.graveyard.append(discarded_card)
            delattr(self.active_player, 'needs_to_discard')  # Remove the flag after discarding

        # Untap lands and creatures
        for card in self.active_player.board:
            card.untap()
            if "creature" in card.card_type.lower():
                card.summoning_sick = False

        # Active player draws a card
        self.active_player.draw_card()

        # Upkeep actions (none for now)
        self.upkeep()

        print(f"{self.active_player.name}'s hand:", ", ".join(map(str, self.active_player.hand)))

    def pre_combat_main_phase(self):
        lands = [card for card in self.active_player.hand if "land" in card.card_type.lower()]
        creatures = [card for card in self.active_player.hand if "creature" in card.card_type.lower()]

        # Play a land if possible
        if lands and not self.active_player.played_land_this_turn:
            land = lands[0]
            self.active_player.play_card(land)
            print(f"{land.name} played. Mana Pool: {self.active_player.mana_pool}")  # Debug

        # Play a creature if possible
        for creature in creatures:
            if all(self.active_player.mana_pool[color] >= amount for color, amount in creature.mana_cost.items()):
                self.active_player.play_card(creature)
                print(f"{creature.name} played. Mana Pool: {self.active_player.mana_pool}")  # Debug
                break

        print(
            f"{self.active_player.name}'s board after pre-combat main phase: {[c.name for c in self.active_player.board]}")  # Debug

    def declare_attackers(self):
        for creature in self.active_player.board:
            if "creature" in creature.card_type.lower() and creature.status == "untapped" and not creature.summoning_sick:
                self.attack_with(creature)

    def declare_blockers(self):
        if self.active_player.attackers:
            attacker = self.active_player.attackers[0]
            for creature in self.non_active_player.board:
                if "creature" in creature.card_type.lower() and creature.status == "untapped":
                    self.block_with(creature, attacker)
                    break

    def combat_phase(self):
        self.declare_attackers()
        self.declare_blockers()

        if self.active_player.attackers:
            print(f"{self.active_player.name} is attacking with {self.active_player.attackers[0].name}")
            if self.non_active_player.blockers:
                print(f"{self.non_active_player.name} is blocking with {self.non_active_player.blockers[0].name}")
                self.combat(self.active_player.attackers[0], self.non_active_player.blockers[0])
            else:
                print(f"{self.non_active_player.name} did not block.")
                if isinstance(self.active_player.attackers[0], CreatureCard):
                    self.non_active_player.life -= self.active_player.attackers[0].power
                else:
                    print(f"Error: Trying to attack with a non-creature card: {self.active_player.attackers[0].name}")
                print(
                    f"{self.non_active_player.name} takes {self.active_player.attackers[0].power} damage. Remaining life: {self.non_active_player.life}")
        else:
            print(f"{self.active_player.name} did not attack.")

    def post_combat_main_phase(self):
        pass

    def ending_phase(self):
        for creature in self.active_player.board:
            if creature.card_type == "creature":
                creature.damage = 0

        while len(self.active_player.hand) > 7:
            discarded_card = self.active_player.hand.pop()
            self.active_player.graveyard.append(discarded_card)

    def attack_with(self, creature):
        if creature in self.active_player.board and creature.status == "untapped" and not creature.summoning_sick:
            self.active_player.attackers.append(creature)
            creature.tap()

    def block_with(self, blocker, attacker):
        if blocker in self.non_active_player.board and blocker.status == "untapped":
            self.non_active_player.blockers.append(blocker)
            blocker.tap()

    def combat(self, attacker, blocker):
        # Calculate combat damage
        attacker_damage_after_combat = attacker.power
        blocker_damage_after_combat = blocker.power

        # Apply damage to blocker and check for lethal damage
        blocker.damage += attacker_damage_after_combat
        if blocker.damage >= blocker.toughness:
            self.non_active_player.board.remove(blocker)
            print(f"{blocker.name} died in combat.")

        # Apply damage to attacker and check for lethal damage
        attacker.damage += blocker_damage_after_combat
        if attacker.damage >= attacker.toughness:
            self.active_player.board.remove(attacker)
            print(f"{attacker.name} died in combat.")

        attacker.tap()


class MTGGame:
    def __init__(self, player1_deck, player2_deck, card_catalog):
        self.card_catalog = card_catalog
        self.player1 = Player(player1_deck, card_catalog, name="Player 1")
        self.player2 = Player(player2_deck, card_catalog, name="Player 2")
        self.board_state = BoardState(self.player1, self.player2)

    def game_initialization(self):
        # Ensure both players have decks
        if not self.player1.deck or not self.player2.deck:
            raise ValueError("Both players must have a deck to play")

        print_deck_details(self.player1.deck)
        print_deck_details(self.player2.deck)

        # Draw starting hands for each player
        for _ in range(7):
            self.player1.draw_card()
            self.player2.draw_card()

        # Print the player's hands in a more readable format
        print(f"{self.player1.name}'s hand:", ", ".join(map(str, self.player1.hand)))
        print(f"{self.player2.name}'s hand:", ", ".join(map(str, self.player2.hand)))

        # Check if either player has no land in their starting hand
        for player in [self.player1, self.player2]:
            if not any(card.card_type == "land" for card in player.hand):
                player.needs_to_discard = True  # Set a flag indicating that the player needs to discard

        # Set initial life totals (this can be done inside the Player's __init__ method too)
        self.player1.life = 20
        self.player2.life = 20

        # Randomly decide which player goes first
        self.active_player = random.choice([self.player1, self.player2])
        if self.active_player == self.player1:
            self.non_active_player = self.player2
        else:
            self.non_active_player = self.player1

        # Initialize board state
        self.board_state = BoardState(self.active_player, self.non_active_player)

    def check_win_condition(self):
        if self.player1.life <= 0:
            return self.player2
        elif self.player2.life <= 0:
            return self.player1
        else:
            return None

    def game_loop(self):
        self.game_initialization()

        winner = None
        while not winner:
            self.board_state.simulate_turn()
            winner = self.check_win_condition()
            sleep(1)

        print(self.player1.name + f" remaining life: {self.player1.life}")
        print(self.player2.name + f" remaining life: {self.player2.life}")
        print(f"{winner.name} has won the game!")
