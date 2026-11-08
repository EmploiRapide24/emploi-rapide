-- Emploi Rapide 24 : alertes par e-mail
create table if not exists public.abonnements (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  email text not null,
  criteres jsonb not null default '{}'::jsonb,
  libelle text check (char_length(libelle) <= 200),
  actif boolean not null default true,
  jeton uuid not null default gen_random_uuid(),
  dernier_envoi text,
  created_at timestamptz not null default now()
);
create index if not exists abonnements_actif_idx on public.abonnements (actif);
alter table public.abonnements enable row level security;

drop policy if exists "mes abonnements" on public.abonnements;
create policy "mes abonnements" on public.abonnements for select to authenticated using (user_id = auth.uid());
drop policy if exists "ajout abonnement" on public.abonnements;
create policy "ajout abonnement" on public.abonnements for insert to authenticated
  with check (user_id = auth.uid() and lower(email) = lower(auth.jwt() ->> 'email'));
drop policy if exists "suppression abonnement" on public.abonnements;
create policy "suppression abonnement" on public.abonnements for delete to authenticated using (user_id = auth.uid());

revoke all on public.abonnements from anon, authenticated;
grant select (id, email, criteres, libelle, actif, created_at) on public.abonnements to authenticated;
grant insert (email, criteres, libelle) on public.abonnements to authenticated;
grant delete on public.abonnements to authenticated;

-- 10 alertes actives maximum par personne
create or replace function public.limite_abonnements() returns trigger language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.abonnements where user_id = auth.uid() and actif) >= 10 then
    raise exception 'Vous avez déjà 10 alertes par e-mail';
  end if;
  return new;
end $$;
drop trigger if exists limite_abonnements on public.abonnements;
create trigger limite_abonnements before insert on public.abonnements for each row execute function public.limite_abonnements();

-- Envoi chaque matin à 8 h 05 (heure de Dakar = UTC)
create extension if not exists pg_net;
create extension if not exists pg_cron;
select cron.unschedule('alertes-emploi') where exists (select 1 from cron.job where jobname = 'alertes-emploi');
select cron.schedule('alertes-emploi', '5 8 * * *',
  $$ select net.http_post(url := 'https://tmymxnerhhcejbkkptdf.supabase.co/functions/v1/alertes',
       headers := '{"Content-Type":"application/json"}'::jsonb, body := '{}'::jsonb) $$);

select jobname, schedule from cron.job;
grant select, update on public.abonnements to service_role;
