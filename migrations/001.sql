CREATE TABLE IF NOT EXISTS workflow_task(id uuid primary key,tenant_id text not null,thread_id text unique not null,status text not null,created_at timestamptz default now());
CREATE TABLE IF NOT EXISTS memory_record(id uuid primary key,tenant_id text not null,customer_id text,thread_id text,layer text not null,key text not null,text text not null,confidence double precision default 1,provenance jsonb default '{}'::jsonb,created_at timestamptz default now());
CREATE INDEX IF NOT EXISTS memory_scope_idx ON memory_record(tenant_id,customer_id,layer);
CREATE TABLE IF NOT EXISTS action_idempotency(tenant_id text not null,key text not null,status text not null,result jsonb,primary key(tenant_id,key));
CREATE TABLE IF NOT EXISTS approval(id uuid primary key,tenant_id text not null,thread_id text not null,action_hash text not null,status text not null,expires_at timestamptz);
CREATE TABLE IF NOT EXISTS outbox(id uuid primary key,event_type text not null,payload jsonb not null,published_at timestamptz);
CREATE TABLE IF NOT EXISTS audit_event(id bigserial primary key,tenant_id text,event jsonb not null,hash text not null,created_at timestamptz default now());
