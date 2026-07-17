from collections import Counter as ValueCounter

from app.config import MANIFESTATIONS


class Counter:

    def __init__(self):

        self.answers = []

    def add_page(self, page_answers):

        self.answers.extend(page_answers)

    def totals(self):

        counts = ValueCounter(answer for answer in self.answers if answer is not None)

        # Keep every report column present, even when it has no selections.
        return {heading: counts[heading] for heading in MANIFESTATIONS}

    def unanswered(self):

        return sum(answer is None for answer in self.answers)
