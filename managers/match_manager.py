from classes.MatchResult import Match, MatchResult
from queries.match_queries import get_matches


def get_match_results(date_of_matches):
    matches = get_matches(date_of_matches)

    matches_per_tour = []

    if len(matches.index) != 0:
        tournaments = matches["tournament_name"].drop_duplicates().tolist()

        for tour in tournaments:
            matches_in_tour = matches[matches["tournament_name"] == tour]
            list_of_matches = [(Match(row))
                               for index, row in matches_in_tour.iterrows()]

            match_result = MatchResult(tour, list_of_matches)

            matches_per_tour.append(match_result)

    return matches_per_tour
