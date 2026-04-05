-- AuraFit Initial Schema Migration
-- Tables ordered by foreign-key dependencies so this file can be executed as-is.
-- Uses IF NOT EXISTS / ON CONFLICT guards for idempotency.

-- ============================================================================
-- SEQUENCES
-- ============================================================================

CREATE SEQUENCE IF NOT EXISTS tenants_id_seq;
CREATE SEQUENCE IF NOT EXISTS users_id_seq;
CREATE SEQUENCE IF NOT EXISTS roles_id_seq;
CREATE SEQUENCE IF NOT EXISTS body_metrics_id_seq;
CREATE SEQUENCE IF NOT EXISTS exercises_id_seq;
CREATE SEQUENCE IF NOT EXISTS goals_id_seq;
CREATE SEQUENCE IF NOT EXISTS notifications_id_seq;
CREATE SEQUENCE IF NOT EXISTS nutrition_logs_id_seq;
CREATE SEQUENCE IF NOT EXISTS progress_photos_id_seq;
CREATE SEQUENCE IF NOT EXISTS subscriptions_id_seq;
CREATE SEQUENCE IF NOT EXISTS payments_id_seq;
CREATE SEQUENCE IF NOT EXISTS workout_logs_id_seq;
CREATE SEQUENCE IF NOT EXISTS workout_exercises_id_seq;

-- ============================================================================
-- 1. TENANTS  (no FK dependencies)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.tenants (
    id              bigint    NOT NULL DEFAULT nextval('tenants_id_seq'::regclass),
    name            varchar   NOT NULL,
    email           varchar   NOT NULL UNIQUE,
    logo_url        text,
    primary_color   varchar,
    secondary_color varchar,
    custom_domain   varchar,
    ai_enabled      boolean   DEFAULT false,
    created_at      timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT tenants_pkey PRIMARY KEY (id)
);

-- ============================================================================
-- 2. USERS  (FK -> tenants)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.users (
    id                 bigint    NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    auth_id            uuid      UNIQUE,
    tenant_id          bigint    NOT NULL,
    email              varchar   NOT NULL,
    password_hash      text      NOT NULL,
    role               varchar   NOT NULL,
    is_email_verified  boolean   DEFAULT false,
    two_factor_enabled boolean   DEFAULT false,
    created_at         timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT fk_users_tenant FOREIGN KEY (tenant_id) REFERENCES public.tenants(id)
);

-- ============================================================================
-- 3. ROLES  (FK -> tenants)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.roles (
    id          bigint  NOT NULL DEFAULT nextval('roles_id_seq'::regclass),
    tenant_id   bigint  NOT NULL,
    role_name   varchar NOT NULL,
    description text,
    CONSTRAINT roles_pkey PRIMARY KEY (id),
    CONSTRAINT roles_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id)
);

-- ============================================================================
-- 4. USER_ROLES  (FK -> users, roles)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.user_roles (
    user_id bigint NOT NULL,
    role_id bigint NOT NULL,
    CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id),
    CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
    CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id)
);

-- ============================================================================
-- 5. BODY_METRICS  (FK -> tenants, users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.body_metrics (
    id                  bigint    NOT NULL DEFAULT nextval('body_metrics_id_seq'::regclass),
    tenant_id           bigint    NOT NULL,
    user_id             bigint    NOT NULL,
    weight              numeric,
    height              numeric,
    body_fat_percentage numeric,
    recorded_at         timestamp NOT NULL,
    created_at          timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT body_metrics_pkey PRIMARY KEY (id),
    CONSTRAINT body_metrics_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT body_metrics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- ============================================================================
-- 6. EXERCISES  (FK -> tenants)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.exercises (
    id           bigint    NOT NULL DEFAULT nextval('exercises_id_seq'::regclass),
    tenant_id    bigint    NOT NULL,
    name         varchar   NOT NULL,
    muscle_group varchar,
    equipment    varchar,
    instructions text,
    created_at   timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT exercises_pkey PRIMARY KEY (id),
    CONSTRAINT exercises_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id)
);

-- ============================================================================
-- 7. GOALS  (FK -> tenants, users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.goals (
    id           bigint  NOT NULL DEFAULT nextval('goals_id_seq'::regclass),
    tenant_id    bigint  NOT NULL,
    user_id      bigint  NOT NULL,
    goal_type    varchar,
    target_value numeric,
    start_date   date,
    end_date     date,
    status       varchar,
    CONSTRAINT goals_pkey PRIMARY KEY (id),
    CONSTRAINT goals_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT goals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- ============================================================================
-- 8. WORKOUT_LOGS  (FK -> tenants, users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.workout_logs (
    id           bigint    NOT NULL DEFAULT nextval('workout_logs_id_seq'::regclass),
    tenant_id    bigint    NOT NULL,
    user_id      bigint    NOT NULL,
    workout_date date      NOT NULL,
    notes        text,
    created_at   timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT workout_logs_pkey PRIMARY KEY (id),
    CONSTRAINT workout_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT workout_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- ============================================================================
-- 9. WORKOUT_EXERCISES  (FK -> workout_logs)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.workout_exercises (
    id               bigint  NOT NULL DEFAULT nextval('workout_exercises_id_seq'::regclass),
    workout_log_id   bigint  NOT NULL,
    exercise_name    varchar NOT NULL,
    sets             integer,
    reps             integer,
    weight           numeric,
    duration_minutes integer,
    rpe              integer,
    CONSTRAINT workout_exercises_pkey PRIMARY KEY (id),
    CONSTRAINT workout_exercises_workout_log_id_fkey FOREIGN KEY (workout_log_id) REFERENCES public.workout_logs(id)
);

-- ============================================================================
-- 10. NUTRITION_LOGS  (FK -> tenants, users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.nutrition_logs (
    id        bigint    NOT NULL DEFAULT nextval('nutrition_logs_id_seq'::regclass),
    tenant_id bigint    NOT NULL,
    user_id   bigint    NOT NULL,
    meal_type varchar,
    calories  integer,
    protein   numeric,
    carbs     numeric,
    fats      numeric,
    logged_at timestamp NOT NULL,
    CONSTRAINT nutrition_logs_pkey PRIMARY KEY (id),
    CONSTRAINT nutrition_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT nutrition_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- ============================================================================
-- 11. PROGRESS_PHOTOS  (FK -> tenants, users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.progress_photos (
    id          bigint    NOT NULL DEFAULT nextval('progress_photos_id_seq'::regclass),
    tenant_id   bigint    NOT NULL,
    user_id     bigint    NOT NULL,
    image_url   text      NOT NULL,
    uploaded_at timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT progress_photos_pkey PRIMARY KEY (id),
    CONSTRAINT progress_photos_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT progress_photos_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- ============================================================================
-- 12. NOTIFICATIONS  (FK -> tenants, users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.notifications (
    id         bigint    NOT NULL DEFAULT nextval('notifications_id_seq'::regclass),
    tenant_id  bigint    NOT NULL,
    user_id    bigint    NOT NULL,
    title      varchar,
    message    text,
    is_read    boolean   DEFAULT false,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT notifications_pkey PRIMARY KEY (id),
    CONSTRAINT notifications_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- ============================================================================
-- 13. SUBSCRIPTIONS  (FK -> tenants, users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.subscriptions (
    id         bigint  NOT NULL DEFAULT nextval('subscriptions_id_seq'::regclass),
    tenant_id  bigint  NOT NULL,
    user_id    bigint  NOT NULL,
    tier       varchar NOT NULL,
    status     varchar NOT NULL,
    start_date date    NOT NULL,
    end_date   date,
    CONSTRAINT subscriptions_pkey PRIMARY KEY (id),
    CONSTRAINT fk_sub_tenant FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT fk_sub_user FOREIGN KEY (user_id) REFERENCES public.users(id)
);

-- ============================================================================
-- 14. PAYMENTS  (FK -> tenants, users, subscriptions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.payments (
    id              bigint    NOT NULL DEFAULT nextval('payments_id_seq'::regclass),
    tenant_id       bigint    NOT NULL,
    user_id         bigint    NOT NULL,
    subscription_id bigint,
    amount          numeric   NOT NULL,
    payment_status  varchar,
    payment_date    timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT payments_pkey PRIMARY KEY (id),
    CONSTRAINT payments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
    CONSTRAINT payments_subscription_id_fkey FOREIGN KEY (subscription_id) REFERENCES public.subscriptions(id)
);

-- ============================================================================
-- SEED DATA: Reserved platform tenant + 3-tier role definitions
-- ============================================================================

-- Platform tenant (id=1) used to anchor super_admin users
INSERT INTO public.tenants (id, name, email)
VALUES (1, 'AuraFit Platform', 'admin@aurafit.com')
ON CONFLICT (id) DO NOTHING;

-- Advance the sequence past the reserved id
SELECT setval('tenants_id_seq', GREATEST(nextval('tenants_id_seq'), 2));

-- Global role definitions (anchored to the platform tenant)
INSERT INTO public.roles (tenant_id, role_name, description)
SELECT 1, r.role_name, r.description
FROM (VALUES
    ('super_admin', 'Platform-wide administrator with access to all tenants'),
    ('owner',       'Tenant owner / fitness creator who manages their organization'),
    ('member',      'End-user / trainee who tracks fitness within a tenant')
) AS r(role_name, description)
WHERE NOT EXISTS (
    SELECT 1 FROM public.roles
    WHERE roles.tenant_id = 1 AND roles.role_name = r.role_name
);
