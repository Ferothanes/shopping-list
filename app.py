import streamlit as st

from src.inventory import add_item, load_inventory, remove_item
from src.cart_view import render_cart
from src.matcher import (
    SOURCE_MEALDB,
    match_recipes,
    match_recipes_by_ingredient,
    normalize_item,
)
from src.styles import apply_styles

st.set_page_config(page_title="Recipe Finder", page_icon="RF", layout="wide")

apply_styles()

inventory = load_inventory()

view_choice = st.radio(
    "View",
    ["Recipe Finder", "Shopping Cart"],
    horizontal=True,
    label_visibility="collapsed",
)
if view_choice == "Shopping Cart":
    render_cart()
    st.stop()

with st.sidebar:
    st.subheader("Match settings")
    max_missing = st.selectbox("Max missing ingredients", [0, 1, 2, 3, 4, 5], index=3)
    required_ingredient = st.text_input(
        "Must include ingredient", placeholder="e.g. chicken", help="Optional"
    )

    st.subheader("Recipe sources")
    sources = st.multiselect(
        "Sources",
        options=[SOURCE_MEALDB],
        default=[SOURCE_MEALDB],
    )

st.title("Recipe Finder")
st.caption("Find recipes based on what you already have in your kitchen.")


fridge_container = st.container()
with fridge_container:
    with st.expander("Your fridge", expanded=True):
        search_query = st.text_input(
            "Search fridge items", placeholder="Type to search", label_visibility="visible"
        )
        if search_query.strip():
            matches = [item for item in inventory if search_query.lower() in item.lower()]
            if matches:
                st.success(f"Found: {', '.join(matches)}")
            else:
                st.warning("No matching items in your fridge.")

        with st.form("add_item_form", clear_on_submit=True):
            add_col1, add_col2 = st.columns([5, 1])
            with add_col1:
                new_item = st.text_input(
                    "Add item", placeholder="e.g. chicken", label_visibility="collapsed"
                )
            with add_col2:
                submitted = st.form_submit_button("Add", use_container_width=True)
            if submitted and new_item.strip():
                add_item(new_item)
                st.rerun()

        if inventory:
            for row_start in range(0, len(inventory), 5):
                row_items = inventory[row_start : row_start + 5]
                row_cols = st.columns(5)
                for col, item in zip(row_cols, row_items):
                    with col:
                        item_cols = st.columns([4, 1])
                        with item_cols[0]:
                            st.markdown(
                                f"<div class='item-chip'>{item}</div>",
                                unsafe_allow_html=True,
                            )
                        with item_cols[1]:
                            if st.button("x", key=f"remove_{row_start}_{item}"):
                                remove_item(item)
                                st.rerun()
        else:
            st.info("Add some ingredients to start.")

st.subheader("Recipe suggestions")
if not inventory:
    st.warning("Add ingredients to your fridge to see recipes.")
else:
    with st.spinner("Finding the best recipes..."):
        @st.cache_data(show_spinner=False, ttl=600)
        def _cached_matches(items: tuple[str, ...], missing: int, srcs: tuple[str, ...]):
            return match_recipes(items, max_missing=missing, sources=srcs)

        required = normalize_item(required_ingredient)
        if required:
            @st.cache_data(show_spinner=False, ttl=600)
            def _cached_required(req: str, items: tuple[str, ...]):
                return match_recipes_by_ingredient(req, items)

            matches = _cached_required(required, tuple(inventory))
        else:
            matches = _cached_matches(tuple(inventory), max_missing, tuple(sources))

    if not matches:
        st.info("No recipes found with the current filters.")
    else:
        cards = st.columns(3)
        for i, match in enumerate(matches):
            with cards[i % 3]:
                st.markdown(f"### {match.name}")
                st.caption(match.source)
                if match.thumbnail:
                    st.image(match.thumbnail, width=180)

                if match.missing:
                    st.warning(f"Missing ({len(match.missing)}): {', '.join(match.missing)}")
                else:
                    st.success("You have everything for this recipe!")

                st.caption(f"Ingredients: {', '.join(match.ingredients)}")

                if match.details_url:
                    st.link_button("View recipe", match.details_url)
