def get_distance_bins(selected_sport_categories: list[str]) -> tuple:
    """
    Returns distance histogram bins depending on selected sport categories.
    """
    if selected_sport_categories == ["Foot sports"]:
        return (0, 5, 10, 21.097, 42.195, float("inf"))

    if selected_sport_categories == ["Cycle sports"]:
        return (0, 25, 50, 100, 200, float("inf"))

    # multiple categories or other sports
    return (0, 5, 50, 100, 200, float("inf"))
