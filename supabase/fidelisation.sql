-- Emploi Rapide 24 – fidélisation : notifications, récapitulatif hebdomadaire, synchronisation
-- 1. Fréquence des alertes e-mail
alter table public.abonnements add column if not exists frequence text not null default 'jour' check (frequence in ('jour','semaine'));
-- 2. Abonnements aux notifications (Web Push)
create table if not exists public.push_subs (
  endpoint text primary key,
  p256dh text not null,
  auth text not null,
  criteres jsonb not null default '{}'::jsonb,
  dernier_envoi text,
  cree_le timestamptz not null default now()
);
alter table public.push_subs enable row level security;
drop policy if exists "inscription push" on public.push_subs;
create policy "inscription push" on public.push_subs for insert to anon, authenticated with check (length(endpoint) < 600 and endpoint like 'https://%');
grant insert on public.push_subs to anon, authenticated;
grant select, update, delete on public.push_subs to service_role;
-- 3. Favoris et candidatures synchronisés avec le compte
create table if not exists public.sync (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  donnees jsonb not null default '{}'::jsonb,
  maj timestamptz not null default now()
);
alter table public.sync enable row level security;
drop policy if exists "ma synchro" on public.sync;
create policy "ma synchro" on public.sync for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid() and pg_column_size(donnees) < 200000);
grant select, insert, update on public.sync to authenticated;
