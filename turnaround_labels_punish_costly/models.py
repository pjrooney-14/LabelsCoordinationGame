from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import numpy as np
import random

author = 'Patrick Rooney'

doc = """
Labels and Turnarounds under Costly Punishment Regimes
"""


class Constants(BaseConstants):
    name_in_url = 'costpunreg'
    players_per_group = 4
    num_rounds = 12
    bonus = 10
    punish_cost = 10

    # == Sentences for each round == #
    solution1 = ['Earnings are public.', 'Earnings are public', 'earnings are public', 'earnings are public.']
    solution2 = ['Old products have been replaced.', 'Old products have been replaced',
                 'old products have been replaced', 'old products have been replaced.'
                 ]
    solution3 = ['The CEO is on vacation.', 'The CEO is on vacation', 'the ceo is on vacation.',
                 'the ceo is on vacation', 'the Ceo is on vacation', 'the Ceo is on vacation.',
                 'The ceo is on vacation.', 'The ceo is on vacation',
                 ]
    solution4 = ['Inventory is full.', 'Inventory is full', 'inventory is full.', 'inventory is full']

    # == Payoff matrices for treatments == #
    payoff_list = np.array([(200, 200, 200, 200, 200),
                           (150, 210, 210, 210, 210),
                           (100, 160, 220, 220, 220),
                           (50, 110, 170, 230, 230),
                           (0, 60, 120, 180, 240)])


class Subsession(BaseSubsession):

    def creating_session(self):
        if self.round_number == 1:
            # Set Paying Rounds#
            paying_round_a = random.randint(1, Constants.num_rounds/2)
            paying_round_b = random.randint(Constants.num_rounds/2 + 1,  Constants.num_rounds)
            audit_array_a = np.arange(1, 7, 1)
            audit_array_b = np.arange(6, 13, 1)
            random_audit_a = np.random.choice(audit_array_a, 1, replace=False)
            random_audit_b = np.random.choice(audit_array_b, 1, replace=False)
            players = self.get_players()
            for p in players:
                p.paying_round_a = paying_round_a
                p.paying_round_b = paying_round_b
                p.participant.vars['rand_audit_a'] = random_audit_a[0]
                p.random_audit_a = p.participant.vars['rand_audit_a']
                p.participant.vars['rand_audit_b'] = random_audit_b[0]
                p.random_audit_b = p.participant.vars['rand_audit_b']
                p.participant.vars['paying_round_a'] = paying_round_a
                p.participant.vars['paying_round_b'] = paying_round_b
                p.participant.vars['condition'] = 'Initialize'
                p.random = random.randint(0, 1000)
                p.participant.vars['random'] = p.random
            # Assign condition based on random number. #
            for p in players:
                nums = [p.random for p in players]
                ids = [p.id_in_subsession for p in players]
                dictionary = dict(zip(ids, nums))
                print(dictionary)
                sorted_dict = dict(sorted(dictionary.items(), key=lambda x: x[1]))
                player_random_nums = [*sorted_dict]
                midpoint = int(self.session.num_participants / 2)
                if p.id_in_subsession in player_random_nums[:midpoint]:
                    p.participant.vars['condition'] = 'Punish_RandomAudit'
                    p.condition = p.participant.vars['condition']
                if p.id_in_subsession in player_random_nums[midpoint:]:
                    p.participant.vars['condition'] = 'Punish_AllRounds'
                    p.condition = p.participant.vars['condition']
            # Sort into conditions
            for p in players:
                high_players = [p for p in players if p.participant.vars['condition'] == 'Punish_RandomAudit']
                low_players = [p for p in players if p.participant.vars['condition'] == 'Punish_AllRounds']
                group_matrix = []
            # Fill in groups for second part #
                while high_players:
                    new_group = [
                        high_players.pop(),
                        high_players.pop(),
                        high_players.pop(),
                        high_players.pop(),
                    ]
                    group_matrix.append(new_group)

                while low_players:
                    new_group = [
                        low_players.pop(),
                        low_players.pop(),
                        low_players.pop(),
                        low_players.pop(),
                    ]
                    group_matrix.append(new_group)
                self.set_group_matrix(group_matrix)
        else:
            # Maintain previous rounds' groups o/w
            self.group_like_round(self.round_number - 1)  # Group like previous round

    def assign_payoff_display(self):
        players = self.get_players()
        for p in self.get_players():
            payoff_list = [p.participant.payoff_plus_participation_fee() for p in players]
            ids = [p.id_in_subsession for p in players]
            dictionary = dict(zip(ids, payoff_list))
            sorted_dict = dict(sorted(dictionary.items(), key=lambda x: x[1], reverse=True))
            player_ranking = [*sorted_dict]
            p.participant.vars['rank'] = player_ranking.index(p.id_in_subsession) + 1
            five_cutoff = int(self.session.num_participants * (1/8))
            four_cutoff = int(self.session.num_participants * (3/8))
            three_cutoff = int(self.session.num_participants * (5/8))
            if p.id_in_subsession in player_ranking[:five_cutoff]:
                payoff_display = 5.00
            if p.id_in_subsession in player_ranking[five_cutoff:four_cutoff]:
                payoff_display = 4.00
            if p.id_in_subsession in player_ranking[four_cutoff:three_cutoff]:
                payoff_display = 3.00
            if p.id_in_subsession in player_ranking[three_cutoff:]:
                payoff_display = 2.00
            p.payoff_display_str = '{:,.2f}'.format(payoff_display)
            p.participant.vars['payoff_display'] = p.payoff_display_str


class Group(BaseGroup):
    condition = models.StringField()
    min = models.IntegerField()
    first = models.IntegerField()
    second = models.IntegerField()
    third = models.IntegerField()
    fourth = models.IntegerField()
    display_punish_result = models.StringField()

    def punish_regime_display(self):
        players = self.get_players()
        for p in players:
            if p.participant.vars['condition'] == 'Punish_RandomAudit':
                punish_regime = 'after two randomly selected rounds'
                p.participant.vars['punish_regime'] = punish_regime
            if p.participant.vars['condition'] == 'Punish_AllRounds':
                punish_regime = 'after each round'
                p.participant.vars['punish_regime'] = punish_regime

    def set_payoffs(self):
        # == Set Payoffs in Each Round per Group Member == #
        players = self.get_players()
        sentences = [p.total_sentences for p in players]
        votes = [p.vote for p in players]
        vote_sum = votes.count('Yes')
        sent_random = np.random.choice(sentences, 4, replace=False)
        self.min = min(sentences)
        self.first = sent_random[0]
        self.second = sent_random[1]
        self.third = sent_random[2]
        self.fourth = sent_random[3]
        for p in players:
            p.round_earnings = Constants.payoff_list.item((p.total_sentences, self.min))
            p.first_p = Constants.payoff_list.item((self.first, self.min))
            p.second_p = Constants.payoff_list.item((self.second, self.min))
            p.third_p = Constants.payoff_list.item((self.third, self.min))
            p.fourth_p = Constants.payoff_list.item((self.fourth, self.min))
            if vote_sum > 0 and self.min != 4 and p.total_sentences == self.min:
                p.round_earnings = 0
                p.counter = 'A'
            elif p.participant.vars['condition'] == 'Punish_RandomAudit' \
                    and self.subsession.round_number != p.random_audit_a \
                    and self.subsession.round_number != p.random_audit_b:
                p.round_earnings = p.round_earnings
                p.counter = 'X'
            else:
                p.round_earnings = p.round_earnings
                p.counter = 'C'

    def show_result(self):
        players = self.get_players()
        counters = [p.counter for p in players]
        count_a = counters.count('A')
        count_x = counters.count('X')
        if count_a > 0:
            display_punish_result = "At least one employee in the firm voted to punish the lowest contributor(s). " \
                                    "They have earned 0 points for this round. Any employee voting in favor of " \
                                    "punishment has sacrificed 10 points from their original round earnings."
            for p in players:
                if self.min == self.first:
                    p.first_p = 0
                if self.min == self.second:
                    p.second_p = 0
                if self.min == self.third:
                    p.third_p = 0
                if self.min == self.fourth:
                    p.fourth_p = 0
                if p.vote == 'Yes':
                    p.round_earnings = max(p.round_earnings - Constants.punish_cost, 0)
                    p.vote_display = "You voted to punish, which costs 10 points."
                if p.vote == "No":
                    p.vote_display = "You did not vote to punish."
        elif count_x > 0:
            display_punish_result = " "
        else:
            display_punish_result = "No changes have been made to any employee's earnings"
        self.display_punish_result = display_punish_result


class Player(BasePlayer):
    belief_index = models.FloatField()
    random = models.FloatField()
    round_id = models.StringField()
    condition = models.StringField()
    consent = models.StringField(label='', choices=['I consent', 'I consent '], widget=widgets.TextInput)
    paying_round_a = models.IntegerField()
    paying_round_b = models.IntegerField()
    payoff_a = models.IntegerField()
    payoff_b = models.IntegerField()
    random_audit_a = models.IntegerField()
    random_audit_b = models.IntegerField()
    payoff_display_str = models.StringField()
    bonus = models.IntegerField()
    round_earnings = models.IntegerField()
    counter = models.StringField()

    practice_response1 = models.IntegerField(label='', choices=[1], widget=widgets.TextInput)
    practice_response2 = models.IntegerField(label='', choices=[210], widget=widgets.TextInput)
    practice_response3 = models.IntegerField(label='', choices=[0], widget=widgets.TextInput)
    practice_response4 = models.IntegerField(label='', choices=[100], widget=widgets.TextInput)
    practice_response5 = models.IntegerField(label='', choices=[0], widget=widgets.TextInput)
    practice_response6 = models.IntegerField(label='', choices=[200], widget=widgets.TextInput)
    practice_response_a = models.IntegerField(label='', widget=widgets.TextInput)
    practice_response_b = models.IntegerField(label='', widget=widgets.TextInput)
    practice_response_c = models.IntegerField(label='', widget=widgets.TextInput)

    true_false1 = models.StringField(label='', choices=['True'], widget=widgets.TextInput)
    true_false2 = models.StringField(label='', choices=['True'], widget=widgets.TextInput)

    submitted_answer1 = models.StringField(label='Earnings are public.', widget=widgets.TextInput, blank=True)
    submitted_answer2 = models.StringField(label='Old products have been replaced.', widget=widgets.TextInput,
                                           blank=True)
    submitted_answer3 = models.StringField(label='The CEO is on vacation.', widget=widgets.TextInput, blank=True)
    submitted_answer4 = models.StringField(label='Inventory is full.', widget=widgets.TextInput, blank=True)

    is_correct1 = models.BooleanField()
    is_correct2 = models.BooleanField()
    is_correct3 = models.BooleanField()
    is_correct4 = models.BooleanField()
    total_sentences = models.IntegerField()
    min_p = models.IntegerField()
    first_p = models.IntegerField()
    second_p = models.IntegerField()
    third_p = models.IntegerField()
    fourth_p = models.IntegerField()

    reflection = models.StringField(label='', widget=widgets.Textarea, blank=True)

    guess1 = models.IntegerField(label='')
    guess2 = models.IntegerField(label='')
    guess3 = models.IntegerField(label='')
    average_guess = models.FloatField()

    vote = models.StringField(label='', widget=widgets.RadioSelect, choices=['Yes', 'No'])
    vote_display = models.StringField()

    # == Questionnaire variables == #
    age = models.IntegerField(label='', min=0, max=100)
    gender = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['Male', 'Female', 'Non-Binary', 'Prefer not to Disclose']
    )
    race = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['White', 'Black', 'East Asian', 'South Asian', 'Middle Eastern', 'Hispanic', 'Multi-racial', 'Other']
    )
    volunteer = models.StringField(label='', widget=widgets.RadioSelect, choices=['Yes', 'No'])
    donate = models.StringField(label='', widget=widgets.RadioSelect, choices=['Yes', 'No'])
    first_pd_strategy = models.StringField(label='', widget=widgets.TextInput)
    later_pd_strategy = models.StringField(label='', widget=widgets.TextInput)
    zero_opinion = models.StringField(label='', widget=widgets.TextInput)
    four_opinion = models.StringField(label='', widget=widgets.TextInput)
    second_firm_feelings = models.StringField(label='', widget=widgets.TextInput)
    later_second_firm_feelings = models.StringField(label='', widget=widgets.TextInput)

    risk1 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['$7 for certain', '$10 with probability 50%, $2 with probability 50%'],
        blank=True
    )
    risk2 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['$6 for certain', '$10 with probability 50%, $2 with probability 50%'],
        blank=True
    )
    risk3 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['$5 for certain', '$10 with probability 50%, $2 with probability 50%'],
        blank=True
    )
    risk4 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['$4 for certain', '$10 with probability 50%, $2 with probability 50%'],
        blank=True
    )
    risk5 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['$3 for certain', '$10 with probability 50%, $2 with probability 50%'],
        blank=True
    )
    amb1 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['Bag 1 (containing 16 red balls and 4 black balls)', 'Bag 2 (containing 20 balls)'],
        blank=True
    )
    amb2 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['Bag 1 (containing 14 red balls and 6 black balls)', 'Bag 2 (containing 20 balls)'],
        blank=True
    )
    amb3 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['Bag 1 (containing 12 red balls and 8 black balls)', 'Bag 2 (containing 20 balls)'],
        blank=True
    )
    amb4 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['Bag 1 (containing 10 red balls and 10 black balls)', 'Bag 2 (containing 20 balls)'],
        blank=True
    )
    amb5 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['Bag 1 (containing 8 red balls and 12 black balls)', 'Bag 2 (containing 20 balls)'],
        blank=True
    )
    amb6 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['Bag 1 (containing 6 red balls and 14 black balls)', 'Bag 2 (containing 20 balls)'],
        blank=True
    )
    amb7 = models.StringField(
        label='',
        widget=widgets.RadioSelect,
        choices=['Bag 1 (containing 4 red balls and 16 black balls)', 'Bag 2 (containing 20 balls)'],
        blank=True
    )
    risk_payoff = models.FloatField()
    risk_payoff_str = models.StringField()
    amb_payoff = models.FloatField()
    amb_payoff_str = models.StringField()

    open_comments = models.StringField(label='', widget=widgets.Textarea, blank=True)

    debrief_1 = models.StringField(label='', widget=widgets.TextInput, choices=['A'], blank=False)
    debrief_2 = models.StringField(label='', widget=widgets.TextInput, choices=['A'], blank=False)
    debrief_3 = models.StringField(label='', widget=widgets.TextInput, choices=['C'], blank=False)
    debrief_4 = models.StringField(label='', widget=widgets.TextInput, choices=['A'], blank=False)
    debrief_5 = models.StringField(label='', widget=widgets.TextInput, choices=['A'], blank=False)
    debrief_6 = models.StringField(label='', widget=widgets.TextInput, choices=['B'], blank=False)

    confirm_payment = models.StringField(label='', widget=widgets.Textarea, blank=False)

    # == Player Functions == #
    def check_correct(self):
        # == Count number of correct sentences entered in round == #
        self.is_correct1 = (self.submitted_answer1 in Constants.solution1)
        self.is_correct2 = (self.submitted_answer2 in Constants.solution2)
        self.is_correct3 = (self.submitted_answer3 in Constants.solution3)
        self.is_correct4 = (self.submitted_answer4 in Constants.solution4)

    def sum_sentences(self):
        # == Sum number of correct sentences entered in round == #
        self.total_sentences = self.is_correct1 + self.is_correct2 + self.is_correct3 + self.is_correct4

    def set_payoffs(self):
        if self.subsession.round_number == self.participant.vars['paying_round_a']:
            self.payoff_a = round(self.round_earnings, 2)
            self.participant.vars['payoff_a'] = self.payoff_a
            self.payoff = self.payoff_a

        if self.subsession.round_number == self.participant.vars['paying_round_b']:
            self.payoff_b = round(self.round_earnings, 2)
            self.participant.vars['payoff_b'] = self.payoff_b
            self.payoff = self.payoff + self.payoff_b

    def set_guess_bonus(self):
        other_players = self.get_others_in_group()
        sentences = [p.total_sentences for p in other_players]
        sentences.sort()
        guesses = [self.guess1, self.guess2, self.guess3]
        guesses.sort()
        guesses_equal_sentences = (sentences == guesses)
        if guesses_equal_sentences:
            self.participant.vars['bonus'] = Constants.bonus
        else:
            self.participant.vars['bonus'] = 0

    def add_bonus(self):
        if self.participant.vars['bonus'] == Constants.bonus:
            self.payoff = self.payoff + Constants.bonus
        else:
            self.payoff = self.payoff

    def calculate_index(self):
        average_guess = (self.guess1 + self.guess2 + self.guess3) / 3
        self.belief_index = average_guess

    # == Calculate Risk and Ambiguity Aversion Payoffs == #
    def extra_payments(self):
        risk = random.choice([self.risk1, self.risk2, self.risk3, self.risk4, self.risk5])
        risk_dict = {self.risk1: 140, self.risk2: 120, self.risk3: 100, self.risk4: 80, self.risk5: 60}
        amb = random.choice([self.amb1, self.amb2, self.amb3, self.amb4, self.amb5, self.amb6, self.amb7])
        amb_dict = {self.amb1: 80, self.amb2: 70, self.amb3: 60, self.amb4: 50, self.amb5: 40,
                    self.amb6: 30, self.amb7: 20}
        rand1 = random.randint(0, 100)
        rand2 = random.randint(0, 100)

        #== Risk Aversion Payoffs ==#
        if risk == '$10 with probability 50%, $2 with probability 50%':
            if rand1 > 50:
                self.payoff = self.payoff + 200
                self.risk_payoff = 200
            else:
                self.risk_payoff = 40
                self.payoff = self.payoff + 40
        else:
            self.risk_payoff = risk_dict[risk]
            self.payoff = self.payoff + self.risk_payoff

        # == Ambiguity Aversion Payoffs ==#
        if amb == 'Bag 2 (containing 20 balls)':
            if rand1 > rand2:
                self.payoff = self.payoff + 200
                self.amb_payoff = 200
            else:
                self.payoff = self.payoff + 40
                self.amb_payoff = 40
        else:
            amb_val = amb_dict[amb]
            if amb_val > rand2:
                self.payoff = self.payoff + 200
                self.amb_payoff = 200
            else:
                self.payoff = self.payoff + 40
                self.amb_payoff = 40

        self.risk_payoff_str = '{:,.0f}'.format(self.risk_payoff)
        self.participant.vars['risk_payoff'] = self.risk_payoff_str
        self.amb_payoff_str = '{:,.0f}'.format(self.amb_payoff)
        self.participant.vars['amb_payoff'] = self.amb_payoff_str

    pass
