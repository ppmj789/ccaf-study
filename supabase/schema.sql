-- 미지의 CCAF 카드 — 로그인 없는 기기 간 기록 저장
-- Supabase 대시보드 → SQL Editor 에 전체를 붙여 넣고 Run.
--
-- 방식: 기기마다 같은 "동기화 암호"를 입력하면, 앱이 암호의 SHA-256 해시를 열쇠로 기록 한 줄을 읽고 쓴다.
-- 암호 원문은 저장하지 않는다. 테이블은 직접 접근을 막고, 아래 두 함수로만 읽고 쓴다.

-- 예전 강의 노트 앱이 쓰던 테이블 정리
drop table if exists public.progress cascade;

create table if not exists public.study_progress (
  sync_hash  text        primary key check (sync_hash ~ '^[0-9a-f]{64}$'),
  data       jsonb       not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.study_progress enable row level security;
-- 정책을 만들지 않으므로 anon·authenticated 는 테이블을 직접 읽거나 쓸 수 없다.
revoke all on table public.study_progress from anon, authenticated;

create or replace function public.load_progress(p_hash text)
returns jsonb
language sql
security definer
set search_path = public
as $$
  select data from public.study_progress where sync_hash = p_hash;
$$;

create or replace function public.save_progress(p_hash text, p_data jsonb)
returns timestamptz
language plpgsql
security definer
set search_path = public
as $$
declare
  t timestamptz;
begin
  if p_hash !~ '^[0-9a-f]{64}$' then
    raise exception 'invalid sync key';
  end if;
  if pg_column_size(p_data) > 1000000 then
    raise exception 'progress too large';
  end if;
  insert into public.study_progress (sync_hash, data, updated_at)
  values (p_hash, p_data, now())
  on conflict (sync_hash) do update set data = excluded.data, updated_at = now()
  returning updated_at into t;
  return t;
end;
$$;

revoke all on function public.load_progress(text) from public;
revoke all on function public.save_progress(text, jsonb) from public;
grant execute on function public.load_progress(text) to anon, authenticated;
grant execute on function public.save_progress(text, jsonb) to anon, authenticated;
