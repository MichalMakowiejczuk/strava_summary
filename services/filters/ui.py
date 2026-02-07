import streamlit as st

from services.filters.logic import (
    filter_by_category,
    filter_by_subcategory,
    get_subcategories,
)

SPORT_CATEGORIES = [
    "Foot sports",
    "Cycle sports",
    "Water sports",
    "Winter sports",
    "Other",
]


def apply_activity_filters(df):
    """
    Renders filter UI and returns:
    - filtered dataframe
    - selected sport categories
    """
    col_category, col_subcategory = st.columns([4, 6])

    # --- CATEGORY ---
    with col_category:
        selected_categories = st.multiselect(
            "Filter by Sport Category:",
            options=SPORT_CATEGORIES,
            default=SPORT_CATEGORIES,
        )

    df = filter_by_category(df, selected_categories)

    # --- SUBCATEGORY ---
    with col_subcategory:
        if len(selected_categories) == 1:
            category = selected_categories[0]
            subcategories = get_subcategories(category)

            selected_sub = st.multiselect(
                f"Filter by {category} type:",
                options=subcategories,
                default=subcategories,
            )

            df = filter_by_subcategory(df, selected_sub)

    return df, selected_categories
