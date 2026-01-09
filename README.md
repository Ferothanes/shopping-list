# Shopping List

Simple Streamlit app for managing your fridge and shopping cart, plus recipe matching.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) update `.env` for API base URL or Supabase credentials.

## Run
```bash
streamlit run app.py
```

## Supabase (persistent storage)
Use Supabase so your fridge and shopping cart persist on Streamlit Cloud.

1. Create a Supabase project.
2. Create tables:
   ```sql
   create table inventory_items (item text primary key);
   create table shopping_cart_items (item text primary key);
   ```
3. Enable Row Level Security and add policies (or disable RLS for a private project):
   ```sql
   alter table inventory_items enable row level security;
   alter table shopping_cart_items enable row level security;

   create policy "inventory read" on inventory_items for select using (true);
   create policy "inventory write" on inventory_items for insert with check (true);
   create policy "inventory delete" on inventory_items for delete using (true);

   create policy "cart read" on shopping_cart_items for select using (true);
   create policy "cart write" on shopping_cart_items for insert with check (true);
   create policy "cart delete" on shopping_cart_items for delete using (true);
   ```
4. Set these in `.env` or Streamlit secrets:
   ```
   SUPABASE_URL=...
   SUPABASE_ANON_KEY=...
   ```
