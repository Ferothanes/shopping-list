import streamlit as st

from src.cart import add_to_cart, load_cart, remove_from_cart
from src.inventory import add_item, load_inventory, remove_item


def render_cart() -> None:
    inventory = load_inventory()
    cart_items = load_cart()

    st.title("Shopping Cart")
    st.caption("Move items from your fridge into your shopping list.")

    top_col_left, top_col_right = st.columns([1, 1])

    with top_col_left:
        with st.container():
            with st.expander("Fridge items", expanded=True):
                if not inventory:
                    st.info("Your fridge is empty.")
                else:
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
                                    if st.button(">", key=f"to_cart_{row_start}_{item}"):
                                        remove_item(item)
                                        add_to_cart(item)
                                        st.rerun()

    with top_col_right:
        with st.container():
            with st.expander("Shopping list", expanded=True):
                remove_mode = st.radio(
                    "When removing from cart",
                    ["Return to fridge", "Remove only"],
                    horizontal=True,
                )
                with st.form("add_cart_form", clear_on_submit=True):
                    add_col1, add_col2 = st.columns([5, 1])
                    with add_col1:
                        new_cart_item = st.text_input(
                            "Add to cart",
                            placeholder="e.g. butter",
                            label_visibility="collapsed",
                        )
                    with add_col2:
                        submitted = st.form_submit_button("Add", use_container_width=True)
                    if submitted and new_cart_item.strip():
                        add_to_cart(new_cart_item)
                        st.rerun()

                if not cart_items:
                    st.info("Your shopping list is empty.")
                else:
                    for row_start in range(0, len(cart_items), 5):
                        row_items = cart_items[row_start : row_start + 5]
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
                                    if st.button("x", key=f"remove_cart_{row_start}_{item}"):
                                        remove_from_cart(item)
                                        if remove_mode == "Return to fridge":
                                            add_item(item)
                                        st.rerun()
