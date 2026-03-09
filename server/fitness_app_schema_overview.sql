-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.body_metrics (
  id bigint NOT NULL DEFAULT nextval('body_metrics_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  user_id bigint NOT NULL,
  weight numeric,
  height numeric,
  body_fat_percentage numeric,
  recorded_at timestamp without time zone NOT NULL,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT body_metrics_pkey PRIMARY KEY (id),
  CONSTRAINT body_metrics_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
  CONSTRAINT body_metrics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.exercises (
  id bigint NOT NULL DEFAULT nextval('exercises_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  name character varying NOT NULL,
  muscle_group character varying,
  equipment character varying,
  instructions text,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT exercises_pkey PRIMARY KEY (id),
  CONSTRAINT exercises_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id)
);
CREATE TABLE public.goals (
  id bigint NOT NULL DEFAULT nextval('goals_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  user_id bigint NOT NULL,
  goal_type character varying,
  target_value numeric,
  start_date date,
  end_date date,
  status character varying,
  CONSTRAINT goals_pkey PRIMARY KEY (id),
  CONSTRAINT goals_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
  CONSTRAINT goals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.notifications (
  id bigint NOT NULL DEFAULT nextval('notifications_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  user_id bigint NOT NULL,
  title character varying,
  message text,
  is_read boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT notifications_pkey PRIMARY KEY (id),
  CONSTRAINT notifications_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
  CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.nutrition_logs (
  id bigint NOT NULL DEFAULT nextval('nutrition_logs_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  user_id bigint NOT NULL,
  meal_type character varying,
  calories integer,
  protein numeric,
  carbs numeric,
  fats numeric,
  logged_at timestamp without time zone NOT NULL,
  CONSTRAINT nutrition_logs_pkey PRIMARY KEY (id),
  CONSTRAINT nutrition_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
  CONSTRAINT nutrition_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.payments (
  id bigint NOT NULL DEFAULT nextval('payments_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  user_id bigint NOT NULL,
  subscription_id bigint,
  amount numeric NOT NULL,
  payment_status character varying,
  payment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT payments_pkey PRIMARY KEY (id),
  CONSTRAINT payments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
  CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT payments_subscription_id_fkey FOREIGN KEY (subscription_id) REFERENCES public.subscriptions(id)
);
CREATE TABLE public.progress_photos (
  id bigint NOT NULL DEFAULT nextval('progress_photos_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  user_id bigint NOT NULL,
  image_url text NOT NULL,
  uploaded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT progress_photos_pkey PRIMARY KEY (id),
  CONSTRAINT progress_photos_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
  CONSTRAINT progress_photos_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.roles (
  id bigint NOT NULL DEFAULT nextval('roles_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  role_name character varying NOT NULL,
  description text,
  CONSTRAINT roles_pkey PRIMARY KEY (id),
  CONSTRAINT roles_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id)
);
CREATE TABLE public.subscriptions (
  id bigint NOT NULL DEFAULT nextval('subscriptions_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  user_id bigint NOT NULL,
  tier character varying NOT NULL,
  status character varying NOT NULL,
  start_date date NOT NULL,
  end_date date,
  CONSTRAINT subscriptions_pkey PRIMARY KEY (id),
  CONSTRAINT fk_sub_tenant FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
  CONSTRAINT fk_sub_user FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.tenants (
  id bigint NOT NULL DEFAULT nextval('tenants_id_seq'::regclass),
  name character varying NOT NULL,
  email character varying NOT NULL UNIQUE,
  logo_url text,
  primary_color character varying,
  secondary_color character varying,
  custom_domain character varying,
  ai_enabled boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT tenants_pkey PRIMARY KEY (id)
);
CREATE TABLE public.user_roles (
  user_id bigint NOT NULL,
  role_id bigint NOT NULL,
  CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id),
  CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id)
);
CREATE TABLE public.users (
  id bigint NOT NULL DEFAULT nextval('users_id_seq'::regclass),
  auth_id uuid UNIQUE,
  tenant_id bigint NOT NULL,
  email character varying NOT NULL,
  password_hash text NOT NULL,
  role character varying NOT NULL,
  is_email_verified boolean DEFAULT false,
  two_factor_enabled boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT fk_users_tenant FOREIGN KEY (tenant_id) REFERENCES public.tenants(id)
);
CREATE TABLE public.workout_exercises (
  id bigint NOT NULL DEFAULT nextval('workout_exercises_id_seq'::regclass),
  workout_log_id bigint NOT NULL,
  exercise_name character varying NOT NULL,
  sets integer,
  reps integer,
  weight numeric,
  duration_minutes integer,
  rpe integer,
  CONSTRAINT workout_exercises_pkey PRIMARY KEY (id),
  CONSTRAINT workout_exercises_workout_log_id_fkey FOREIGN KEY (workout_log_id) REFERENCES public.workout_logs(id)
);
CREATE TABLE public.workout_logs (
  id bigint NOT NULL DEFAULT nextval('workout_logs_id_seq'::regclass),
  tenant_id bigint NOT NULL,
  user_id bigint NOT NULL,
  workout_date date NOT NULL,
  notes text,
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT workout_logs_pkey PRIMARY KEY (id),
  CONSTRAINT workout_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
  CONSTRAINT workout_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
