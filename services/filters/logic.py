from services.constants import SPORT_CATEGORY_MAP


def filter_by_category(df, selected_categories):
    if not selected_categories:
        return df.iloc[0:0]
    return df[df["sport_category"].isin(selected_categories)]


def get_subcategories(category):
    return [sport for sport, cat in SPORT_CATEGORY_MAP.items() if cat == category]


def filter_by_subcategory(df, selected_subcategories):
    if not selected_subcategories:
        return df.iloc[0:0]
    return df[df["sport_type"].isin(selected_subcategories)]
